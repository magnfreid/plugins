---
name: dio
description: Flutter HTTP client setup with Dio — AppHttpClient wrapper, interceptors (auth, retry, logging), error mapping to domain exceptions, per-layer client wiring in bootstrap.dart, and API service consumption patterns. Trigger on "http client", "API call", "network request", "Dio setup", "interceptor", "retry logic", "base URL config", or any networking layer work in a Flutter app.
---

# dio

Conventions for HTTP networking in this Flutter stack: Dio as the HTTP client, one configured client per API layer, interceptors for cross-cutting concerns, domain exceptions instead of raw `DioException`.

## Packages

```yaml
dependencies:
  dio: ^5.0.0
  dio_smart_retry: ^7.0.0

dev_dependencies:
  pretty_dio_logger: ^1.4.0
```

`dio_smart_retry` handles retry with backoff out of the box — don't roll a custom retry interceptor. `pretty_dio_logger` is dev-only; never ship it in release builds.

## AppHttpClient — the configured wrapper

One class that owns a `Dio` instance. It accepts configuration, wires interceptors, and exposes the `Dio` for services to use directly. The point is a single place per API layer to control timeouts, headers, and behavior — not to abstract away Dio's API.

```dart
import 'package:dio/dio.dart';

class AppHttpClient {
  AppHttpClient({
    required String baseUrl,
    this.connectTimeout = const Duration(seconds: 10),
    this.receiveTimeout = const Duration(seconds: 15),
    this.sendTimeout = const Duration(seconds: 15),
    Map<String, String> headers = const {},
    List<Interceptor> interceptors = const [],
  }) : dio = Dio(
          BaseOptions(
            baseUrl: baseUrl,
            connectTimeout: connectTimeout,
            receiveTimeout: receiveTimeout,
            sendTimeout: sendTimeout,
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json',
              ...headers,
            },
          ),
        ) {
    dio.interceptors.addAll(interceptors);
  }

  final Dio dio;
  final Duration connectTimeout;
  final Duration receiveTimeout;
  final Duration sendTimeout;
}
```

`dio` is public. Services receive it directly and use standard Dio methods (`get`, `post`, etc.). No reason to proxy every HTTP verb through the wrapper — that's busywork that adds nothing.

### Why a class and not just a factory function?

You might only need a factory function today, but the class gives you a place to hang lifecycle methods later (e.g., `dispose()` to cancel in-flight requests, or a method to swap auth tokens at runtime). Start with the class; it costs nothing.

## Interceptors

Interceptors are the primary extension point. Each one is a separate class, single-purpose.

### Order matters

Interceptors run in the order they're added. Recommended order:

1. **AuthInterceptor** — attaches tokens before the request leaves.
2. **RetryInterceptor** — retries on transient failures (must see the final request, including auth headers).
3. **ErrorMappingInterceptor** — translates `DioException` to domain exceptions (runs last so retries are already exhausted).
4. **LogInterceptor** (debug only) — logs the final request/response after all transformations.

### AuthInterceptor

Reads the current token and attaches it. If the token is expired and you have a refresh mechanism, handle refresh here with a lock to prevent concurrent refresh races.

```dart
import 'package:dio/dio.dart';

class AuthInterceptor extends Interceptor {
  AuthInterceptor({required this.tokenProvider});

  /// Returns the current access token, or null if unauthenticated.
  final Future<String?> Function() tokenProvider;

  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    final token = await tokenProvider();
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }
}
```

`tokenProvider` is a callback, not a direct dependency on an auth repository. This keeps the interceptor decoupled — it doesn't know where tokens come from.

**Token refresh variant** — if you need automatic refresh:

```dart
class AuthInterceptor extends QueuedInterceptor {
  AuthInterceptor({
    required this.tokenProvider,
    required this.refreshToken,
    required this.onAuthFailure,
  });

  final Future<String?> Function() tokenProvider;
  final Future<String> Function() refreshToken;
  final VoidCallback onAuthFailure;

  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    final token = await tokenProvider();
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }

  @override
  Future<void> onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    if (err.response?.statusCode != 401) {
      return handler.next(err);
    }

    try {
      final newToken = await refreshToken();
      final retryOptions = err.requestOptions
        ..headers['Authorization'] = 'Bearer $newToken';

      final response = await Dio().fetch(retryOptions);
      return handler.resolve(response);
    } catch (_) {
      onAuthFailure();
      return handler.reject(err);
    }
  }
}
```

Use `QueuedInterceptor` (not `Interceptor`) for the refresh variant. It serializes concurrent requests during a refresh — without it, multiple 401s trigger multiple refresh calls simultaneously.

### RetryInterceptor (via dio_smart_retry)

Don't write your own. `dio_smart_retry` handles exponential backoff, status code filtering, and retry budgets.

```dart
import 'package:dio_smart_retry/dio_smart_retry.dart';

RetryInterceptor buildRetryInterceptor(Dio dio) {
  return RetryInterceptor(
    dio: dio,
    retries: 3,
    retryDelays: const [
      Duration(seconds: 1),
      Duration(seconds: 2),
      Duration(seconds: 4),
    ],
    retryableExtraStatuses: {408, 429},
  );
}
```

The default retryable statuses already include 500–599 and timeout errors. Add `408` (Request Timeout) and `429` (Too Many Requests) explicitly — they're common in real APIs. For 429, a smarter approach is to read the `Retry-After` header, but the package's fixed delays are a reasonable starting point.

**When NOT to retry:** POST/PUT/PATCH requests that aren't idempotent. If your API doesn't guarantee idempotency on writes, filter retries to GET/DELETE only:

```dart
RetryInterceptor(
  dio: dio,
  retries: 3,
  retryDelays: const [
    Duration(seconds: 1),
    Duration(seconds: 2),
    Duration(seconds: 4),
  ],
  retryEvaluator: (error, attempt) {
    if (error.requestOptions.method == 'GET' ||
        error.requestOptions.method == 'DELETE') {
      return DefaultRetryEvaluator(
        retryableExtraStatuses: {408, 429},
      ).evaluate(error, attempt);
    }
    return false;
  },
);
```

### ErrorMappingInterceptor

Maps `DioException` to domain-specific exceptions so that BLoCs and repositories never import `package:dio`.

```dart
import 'package:dio/dio.dart';

class ErrorMappingInterceptor extends Interceptor {
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    final mapped = switch (err.type) {
      DioExceptionType.connectionTimeout ||
      DioExceptionType.sendTimeout ||
      DioExceptionType.receiveTimeout =>
        NetworkTimeoutException(
          message: 'Request timed out',
          requestOptions: err.requestOptions,
        ),
      DioExceptionType.connectionError =>
        NoConnectionException(
          message: 'No internet connection',
          requestOptions: err.requestOptions,
        ),
      DioExceptionType.badResponse => _mapBadResponse(err),
      _ => ServerException(
            message: err.message ?? 'Unexpected error',
            requestOptions: err.requestOptions,
          ),
    };
    handler.reject(mapped);
  }

  DioException _mapBadResponse(DioException err) {
    final statusCode = err.response?.statusCode;
    final data = err.response?.data;
    final serverMessage = data is Map<String, dynamic>
        ? (data['message'] as String?) ?? (data['error'] as String?)
        : null;

    return switch (statusCode) {
      401 => UnauthorizedException(
          message: serverMessage ?? 'Unauthorized',
          requestOptions: err.requestOptions,
        ),
      403 => ForbiddenException(
          message: serverMessage ?? 'Forbidden',
          requestOptions: err.requestOptions,
        ),
      404 => NotFoundException(
          message: serverMessage ?? 'Not found',
          requestOptions: err.requestOptions,
        ),
      422 => ValidationException(
          message: serverMessage ?? 'Validation failed',
          requestOptions: err.requestOptions,
          errors: data is Map<String, dynamic>
              ? data['errors'] as Map<String, dynamic>?
              : null,
        ),
      _ => ServerException(
          message: serverMessage ?? 'Server error ($statusCode)',
          requestOptions: err.requestOptions,
          statusCode: statusCode,
        ),
    };
  }
}
```

### Domain exception hierarchy

```dart
import 'package:dio/dio.dart';

class ServerException extends DioException {
  ServerException({
    required super.requestOptions,
    required super.message,
    this.statusCode,
  });

  final int? statusCode;
}

class NetworkTimeoutException extends DioException {
  NetworkTimeoutException({
    required super.requestOptions,
    required super.message,
  });
}

class NoConnectionException extends DioException {
  NoConnectionException({
    required super.requestOptions,
    required super.message,
  });
}

class UnauthorizedException extends DioException {
  UnauthorizedException({
    required super.requestOptions,
    required super.message,
  });
}

class ForbiddenException extends DioException {
  ForbiddenException({
    required super.requestOptions,
    required super.message,
  });
}

class NotFoundException extends DioException {
  NotFoundException({
    required super.requestOptions,
    required super.message,
  });
}

class ValidationException extends DioException {
  ValidationException({
    required super.requestOptions,
    required super.message,
    this.errors,
  });

  final Map<String, dynamic>? errors;
}
```

These extend `DioException` so they flow through Dio's error pipeline. Repositories catch these typed exceptions; BLoCs catch the repository's domain exceptions or these directly depending on your layering.

**Alternative:** If you want a completely Dio-free domain layer, make these plain `Exception` subclasses and have the repository catch `DioException` + rethrow as domain exceptions. Tradeoff: more mapping code in every repository method vs. a cleaner domain boundary. For most apps, extending `DioException` is pragmatic enough.

## Bootstrap wiring

Create one `AppHttpClient` per API layer. Each gets its own base URL, timeouts, and interceptor set tailored to that layer's needs.

```dart
// bootstrap.dart

import 'package:dio/dio.dart';
import 'package:dio_smart_retry/dio_smart_retry.dart';
import 'package:flutter/foundation.dart';
import 'package:pretty_dio_logger/pretty_dio_logger.dart';

Future<void> bootstrap() async {
  // --- Auth (needed by interceptors) ---
  final authTokenStorage = AuthTokenStorage();

  // --- Core API client ---
  final coreClient = AppHttpClient(
    baseUrl: const String.fromEnvironment('CORE_API_URL'),
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 15),
    interceptors: [
      AuthInterceptor(tokenProvider: authTokenStorage.getAccessToken),
      // Retry added below — needs the Dio instance
    ],
  );
  coreClient.dio.interceptors.add(buildRetryInterceptor(coreClient.dio));
  coreClient.dio.interceptors.add(const ErrorMappingInterceptor());
  if (kDebugMode) {
    coreClient.dio.interceptors.add(PrettyDioLogger(
      requestHeader: true,
      requestBody: true,
      responseBody: true,
    ));
  }

  // --- Payment API client (different base URL, longer timeouts) ---
  final paymentClient = AppHttpClient(
    baseUrl: const String.fromEnvironment('PAYMENT_API_URL'),
    connectTimeout: const Duration(seconds: 15),
    receiveTimeout: const Duration(seconds: 30),
    interceptors: [
      AuthInterceptor(tokenProvider: authTokenStorage.getAccessToken),
    ],
  );
  paymentClient.dio.interceptors.add(
    RetryInterceptor(
      dio: paymentClient.dio,
      retries: 2, // Fewer retries for payment — idempotency matters
      retryDelays: const [Duration(seconds: 2), Duration(seconds: 5)],
      retryEvaluator: (error, attempt) {
        // Only retry GETs for payment endpoints
        return error.requestOptions.method == 'GET' &&
            DefaultRetryEvaluator(
              retryableExtraStatuses: {408, 429},
            ).evaluate(error, attempt);
      },
    ),
  );
  paymentClient.dio.interceptors.add(const ErrorMappingInterceptor());

  // --- Public API client (no auth) ---
  final publicClient = AppHttpClient(
    baseUrl: const String.fromEnvironment('PUBLIC_API_URL'),
    interceptors: const [ErrorMappingInterceptor()],
  );
  publicClient.dio.interceptors.add(buildRetryInterceptor(publicClient.dio));

  // --- Wire into repositories ---
  // Pass coreClient.dio, paymentClient.dio, etc. to your repository
  // constructors via your DI solution (get_it, provider, manual).
}
```

Note the `RetryInterceptor` needs the `Dio` instance it's attached to (for re-issuing requests). That's why it's added after construction via `dio.interceptors.add()` rather than in the constructor's interceptor list.

### Environment-based base URLs

Use `--dart-define` to inject base URLs at build time:

```bash
flutter run --dart-define=CORE_API_URL=https://api.example.com/v1
```

Access via `const String.fromEnvironment('CORE_API_URL')`. Never hardcode URLs.

For multi-environment setups (dev/staging/prod), use `--dart-define-from-file`:

```bash
flutter run --dart-define-from-file=config/dev.json
```

```json
{
  "CORE_API_URL": "https://dev-api.example.com/v1",
  "PAYMENT_API_URL": "https://dev-payments.example.com/v1"
}
```

## API service pattern

Each API service (or "data source") takes a `Dio` instance — not the `AppHttpClient`. It uses Dio's API directly.

```dart
class UserApiService {
  const UserApiService({required Dio dio}) : _dio = dio;

  final Dio _dio;

  Future<UserDto> getUser(String id) async {
    final response = await _dio.get<Map<String, dynamic>>('/users/$id');
    return UserDto.fromJson(response.data!);
  }

  Future<List<UserDto>> listUsers({int page = 1, int perPage = 20}) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/users',
      queryParameters: {'page': page, 'per_page': perPage},
    );
    final list = response.data!['data'] as List<dynamic>;
    return list
        .cast<Map<String, dynamic>>()
        .map(UserDto.fromJson)
        .toList();
  }

  Future<void> updateUser(String id, UpdateUserRequest request) async {
    await _dio.patch<void>('/users/$id', data: request.toJson());
  }

  Future<void> deleteUser(String id) async {
    await _dio.delete<void>('/users/$id');
  }
}
```

Rules:
- Services return DTOs, not domain models. The repository layer maps DTOs → domain models.
- Type the generic on `get<T>`, `post<T>`, etc. — it tells Dio how to cast `response.data`.
- Services don't catch exceptions. Let them propagate to the repository or BLoC.
- One service per logical API resource (users, orders, etc.), not one per endpoint.

### CancelToken for request cancellation

For requests that should cancel when the user navigates away (e.g., search-as-you-type):

```dart
class SearchApiService {
  SearchApiService({required Dio dio}) : _dio = dio;

  final Dio _dio;
  CancelToken? _cancelToken;

  Future<List<ResultDto>> search(String query) async {
    _cancelToken?.cancel();
    _cancelToken = CancelToken();

    final response = await _dio.get<Map<String, dynamic>>(
      '/search',
      queryParameters: {'q': query},
      cancelToken: _cancelToken,
    );
    final list = response.data!['results'] as List<dynamic>;
    return list
        .cast<Map<String, dynamic>>()
        .map(ResultDto.fromJson)
        .toList();
  }

  void dispose() {
    _cancelToken?.cancel();
  }
}
```

Cancel the previous request before issuing a new one. The cancelled request throws a `DioException` with type `cancel` — the `ErrorMappingInterceptor` should let these pass through or ignore them.

## File layout

```
lib/core/network/
  app_http_client.dart
  interceptors/
    auth_interceptor.dart
    error_mapping_interceptor.dart
    retry.dart              # buildRetryInterceptor factory
  exceptions/
    server_exception.dart   # All domain exception classes
```

API services live in their respective feature or data package:

```
packages/user_api/lib/src/
  user_api_service.dart
  models/
    user_dto.dart
    update_user_request.dart
```

Or if not using packages:

```
lib/features/user/data/
  user_api_service.dart
  models/
    user_dto.dart
```

## Testing

Mock `Dio` using a custom `HttpClientAdapter` or a package like `http_mock_adapter`:

```yaml
dev_dependencies:
  http_mock_adapter: ^0.6.0
```

```dart
import 'package:dio/dio.dart';
import 'package:http_mock_adapter/http_mock_adapter.dart';
import 'package:test/test.dart';

void main() {
  late Dio dio;
  late DioAdapter adapter;
  late UserApiService sut;

  setUp(() {
    dio = Dio(BaseOptions(baseUrl: 'https://api.test.com'));
    adapter = DioAdapter(dio: dio);
    sut = UserApiService(dio: dio);
  });

  test('getUser returns parsed DTO', () async {
    adapter.onGet(
      '/users/123',
      (server) => server.reply(200, {
        'id': '123',
        'name': 'Test User',
        'email': 'test@example.com',
      }),
    );

    final user = await sut.getUser('123');

    expect(user.id, '123');
    expect(user.name, 'Test User');
  });

  test('getUser throws NotFoundException on 404', () async {
    // Add ErrorMappingInterceptor to test the full pipeline
    dio.interceptors.add(const ErrorMappingInterceptor());

    adapter.onGet(
      '/users/999',
      (server) => server.reply(404, {'message': 'User not found'}),
    );

    expect(
      () => sut.getUser('999'),
      throwsA(isA<NotFoundException>()),
    );
  });
}
```

Services take `Dio` as a constructor parameter, so injecting a mock-adapted instance is trivial. No need for an abstract `HttpClient` interface just for testability — the adapter pattern handles it.

## Anti-patterns (do not do)

- **Proxying every Dio method through AppHttpClient** — `client.get(...)`, `client.post(...)` wrappers that just forward to `dio.get(...)`. Pointless indirection. Expose `dio` and let services use it.
- **Creating Dio instances inside services** — services receive a configured `Dio`, they don't create one. This is how you get inconsistent timeouts and missing interceptors.
- **Catching exceptions in API services** — let them propagate. The repository or BLoC decides how to handle errors.
- **Hardcoding base URLs** — use `--dart-define` or `--dart-define-from-file`. Even for a single environment.
- **Logging interceptor in release builds** — `PrettyDioLogger` or `LogInterceptor` must be gated behind `kDebugMode`. Leaking request/response bodies in production is a security risk.
- **Custom retry logic** — `dio_smart_retry` exists and handles edge cases (backoff, status filtering, cancellation). Don't reinvent it.
- **One client per endpoint** — one client per API *layer* or *service boundary* (core, payments, analytics). If two endpoints share a base URL and auth strategy, they share a client.
- **Retrying non-idempotent writes blindly** — POST to create a resource retried on timeout can create duplicates. Filter retries by HTTP method or ensure your API supports idempotency keys.
