---
name: hig
description: How to make SwiftUI UI follow Apple's Human Interface Guidelines and use native components — fetching the live HIG and SwiftUI documentation as JSON, a component-to-page map, and what to check at clarify, plan, and review. Use when a project's CLAUDE.md names it for UI work, or when designing, building, or reviewing SwiftUI views, controls, navigation, or presentation.
---

# Human Interface Guidelines for SwiftUI

How to make SwiftUI UI follow the HIG and use native components, at every step of a change.

**Technique, not choice.** This is how to apply the HIG once a project has opted in. The project's
`CLAUDE.md` and the patterns already in the code win over anything here, and they win without
discussion. This skill carries no minimum OS version and no architecture. Where guidance depends
on the OS version, check the project's deployment target (`IPHONEOS_DEPLOYMENT_TARGET` /
`MACOSX_DEPLOYMENT_TARGET` in `project.pbxproj`, or `platforms:` in `Package.swift`).

## Opting in

The project adds the line "UI work follows `swiftui-toolkit:hig`." to its `CLAUDE.md`. `dev-workflow`
clarify, planner and reviewer then load this skill on UI changes. Outside the workflow it triggers
on its description.

## Fetching the guidelines

**The HTML pages at developer.apple.com are a JavaScript shell, and a plain fetch gets no content.
Always fetch the JSON form.** Two base URLs:

- HIG: `https://developer.apple.com/tutorials/data/design/human-interface-guidelines/<slug>.json`
- Developer docs: `https://developer.apple.com/tutorials/data/documentation/<path>.json`

The command:

```bash
curl -s -g "<url>.json" | python3 -I <this skill's directory>/scripts/doc-text.py
```

`-g` is required because API paths contain parentheses and brackets. This skill's base directory is
the one shown when the skill loads. Without Bash, use WebFetch on the JSON URL and read the fields
below.

| Field | Holds |
|---|---|
| `abstract` | one-sentence summary |
| `primaryContentSections[].content[]` | the body: `heading`, `paragraph` with `inlineContent`, `unorderedList`, `aside` for notes and warnings, `tabNavigator` for platform tabs, `codeListing` |
| `references` | resolves every `identifier` to a `title` and `url` |
| `topicSections[].identifiers` | child pages |
| `metadata.platforms[]` | on API pages: `introducedAt`, and `deprecatedAt` + `message` when deprecated |
| `deprecationSummary` | why and what instead, on deprecated API pages |
| `metadata.customMetadata.alert-date` / `alert-text` | on HIG pages: the last substantive change |

**Read "Platform considerations" and then the heading for the target platform.** General best
practice comes first on the page, and the platform-specific rules come under that heading.

**Check the response, not just the parse.** A wrong slug returns `404` with `text/html`, so a JSON
parse error means the URL is wrong. Check with
`curl -s -o /dev/null -w '%{http_code} %{content_type}'`.

**HIG guidance can describe the newest OS's look.** If a page's `alert-text` mentions a redesign
and the deployment target is older, check the guidance against the oldest supported OS too, and
raise any conflict. Do not name OS versions in this skill.

## Finding a page that is not in the map

Fetch the root `…/design/human-interface-guidelines.json`. Its topics are six section pages:
`getting-started`, `foundations`, `patterns`, `components`, `inputs`, `technologies`. `components`
lists eight subsection pages, and those list the component pages. `doc-text.py` prints each page's
children with their `url`. **The slug is the last path segment of that url.** For API pages, take
the `url` from a type page's topics, drop the leading `/documentation/` (keep any suffix like
`-5w0tj`), and append `.json`.

**Never guess a slug.** A page you cannot reach from an index does not exist. If the map is wrong,
say so in your report so the map gets fixed.

## Component map

HIG slugs resolve against the HIG base URL and doc paths against the developer docs base URL, both
above. Doc paths are relative to `…/documentation/`.

### Components

| Component | HIG slug | Developer docs |
|---|---|---|
| Toolbars | `toolbars` | `swiftui/view/toolbar(content:)`, `swiftui/toolbaritem`, `swiftui/toolbaritemgroup`, `swiftui/toolbaritemplacement` |
| Navigation bars (no page of their own — the HIG covers them under Toolbars) | `toolbars` | `swiftui/navigationstack`, `swiftui/navigationlink`, `swiftui/view/navigationtitle(_:)`, `swiftui/view/navigationbartitledisplaymode(_:)`, `swiftui/view/navigationdestination(for:destination:)` |
| Tab bars | `tab-bars` | `swiftui/tabview`, `swiftui/tab`, `swiftui/view/badge(_:)` |
| Sidebars | `sidebars` | `swiftui/navigationsplitview` |
| Split views | `split-views` | `swiftui/navigationsplitview`, `swiftui/view/inspector(ispresented:content:)` |
| Lists and tables | `lists-and-tables` | `swiftui/list`, `swiftui/table`, `swiftui/section`, `swiftui/view/liststyle(_:)`, `swiftui/view/swipeactions(edge:allowsfullswipe:content:)`, `swiftui/view/refreshable(action:)` |
| Collections | `collections` | `swiftui/lazyvgrid` |
| Scroll views | `scroll-views` | `swiftui/scrollview` |
| Disclosure controls | `disclosure-controls` | `swiftui/disclosuregroup` |
| Labels | `labels` | `swiftui/label`, `swiftui/labeledcontent` |
| Sheets | `sheets` | `swiftui/view/sheet(ispresented:ondismiss:content:)`, `swiftui/view/presentationdetents(_:)`, `swiftui/view/presentationdragindicator(_:)` |
| Alerts | `alerts` | `swiftui/view/alert(_:ispresented:actions:message:)` |
| Action sheets and confirmation dialogs | `action-sheets` | `swiftui/view/confirmationdialog(_:ispresented:titlevisibility:actions:message:)` |
| Popovers | `popovers` | `swiftui/view/popover(ispresented:attachmentanchor:arrowedge:content:)` |
| Menus | `menus` | `swiftui/menu`, `swiftui/controlgroup` |
| Pull-down buttons | `pull-down-buttons` | `swiftui/menu` |
| Pop-up buttons | `pop-up-buttons` | `swiftui/picker` |
| Context menus | `context-menus` | `swiftui/view/contextmenu(menuitems:)` |
| Edit menus | `edit-menus` | — |
| Activity views (share sheet) | `activity-views` | `swiftui/sharelink` |
| Buttons | `buttons` | `swiftui/button`, `swiftui/buttonrole`, `swiftui/view/buttonstyle(_:)`, `swiftui/view/disabled(_:)` |
| Search fields | `search-fields` | `swiftui/view/searchable(text:placement:prompt:)`, `swiftui/view/searchsuggestions(_:)` |
| Text fields | `text-fields` | `swiftui/textfield`, `swiftui/securefield`, `swiftui/view/focused(_:)`, `swiftui/view/scrolldismisseskeyboard(_:)` |
| Text views | `text-views` | `swiftui/texteditor` |
| Pickers | `pickers` | `swiftui/picker`, `swiftui/view/pickerstyle(_:)`, `swiftui/datepicker` |
| Color wells | `color-wells` | `swiftui/colorpicker` |
| Segmented controls | `segmented-controls` | `swiftui/segmentedpickerstyle`, `swiftui/view/pickerstyle(_:)` |
| Toggles | `toggles` | `swiftui/toggle` |
| Sliders | `sliders` | `swiftui/slider` |
| Steppers | `steppers` | `swiftui/stepper` |
| Progress indicators | `progress-indicators` | `swiftui/progressview` |
| Gauges | `gauges` | `swiftui/gauge` |
| Page controls | `page-controls` | `swiftui/tabviewstyle` |
| Charts | `charts` | `charts` |
| Status bars | `status-bars` | `swiftui/view/statusbarhidden(_:)` |
| Widgets | `widgets` | `widgetkit` |
| Notifications | `notifications` | `usernotifications` |
| Live Activities | `live-activities` | `activitykit` |

### Patterns

| Component | HIG slug | Developer docs |
|---|---|---|
| Onboarding | `onboarding` | — |
| Launching and launch screens | `launching` | `bundleresources/information-property-list/uilaunchscreen` |
| Modality and full-screen covers | `modality` | `swiftui/view/fullscreencover(ispresented:ondismiss:content:)` |
| Searching | `searching` | `swiftui/view/searchable(text:placement:prompt:)` |
| Entering data and forms | `entering-data` | `swiftui/form`, `swiftui/view/formstyle(_:)` |
| Settings | `settings` | `swiftui/form` |
| Loading and empty states | `loading` | `swiftui/progressview`, `swiftui/contentunavailableview` |
| Feedback | `feedback` | — |
| Haptics | `playing-haptics` | `swiftui/view/sensoryfeedback(_:trigger:)`, `swiftui/sensoryfeedback` |
| Managing notifications | `managing-notifications` | `usernotifications` |
| Managing accounts | `managing-accounts` | `authenticationservices` |
| Drag and drop | `drag-and-drop` | `swiftui/view/draggable(_:)` |
| Undo and redo | `undo-and-redo` | — |
| Ratings and reviews | `ratings-and-reviews` | `storekit/requestreviewaction` |
| Collaboration and sharing | `collaboration-and-sharing` | `swiftui/sharelink` |
| Multitasking | `multitasking` | — |
| Offering help | `offering-help` | `swiftui/view/help(_:)` |
| File management | `file-management` | — |

### Foundations

| Component | HIG slug | Developer docs |
|---|---|---|
| Accessibility | `accessibility` | `swiftui/view/accessibilitylabel(_:)`, `swiftui/view/accessibilityhint(_:)`, `swiftui/view/accessibilityaddtraits(_:)`, `swiftui/environmentvalues/accessibilityreducemotion` |
| App icons | `app-icons` | `xcode/configuring-your-app-icon` |
| Branding | `branding` | — |
| Color | `color` | `swiftui/color`, `swiftui/view/foregroundstyle(_:)`, `swiftui/view/tint(_:)` |
| Dark mode | `dark-mode` | `swiftui/colorscheme`, `swiftui/environmentvalues/colorscheme`, `swiftui/view/preferredcolorscheme(_:)` |
| Icons | `icons` | — |
| Images | `images` | `swiftui/image` |
| Inclusion | `inclusion` | — |
| Layout | `layout` | `swiftui/view/padding(_:_:)`, `swiftui/view/safeareainset(edge:alignment:spacing:content:)` |
| Materials | `materials` | `swiftui/material` |
| Motion | `motion` | `swiftui/view/animation(_:value:)`, `swiftui/withanimation(_:_:)`, `swiftui/environmentvalues/accessibilityreducemotion` |
| Privacy | `privacy` | `bundleresources/privacy-manifest-files` |
| Right to left | `right-to-left` | `swiftui/layoutdirection` |
| SF Symbols | `sf-symbols` | `swiftui/image`, `swiftui/label`, `swiftui/view/symbolrenderingmode(_:)`, `swiftui/view/symboleffect(_:options:value:)` |
| Typography and Dynamic Type | `typography` | `swiftui/font`, `swiftui/view/font(_:)`, `swiftui/dynamictypesize`, `swiftui/view/dynamictypesize(_:)` |
| Writing | `writing` | — |

### Inputs and technologies

| Component | HIG slug | Developer docs |
|---|---|---|
| Gestures | `gestures` | — |
| Keyboards and shortcuts | `keyboards` | `swiftui/view/keyboardshortcut(_:modifiers:)` |
| VoiceOver | `voiceover` | `swiftui/view/accessibilitylabel(_:)` |
| Sign in with Apple | `sign-in-with-apple` | `authenticationservices` |

### Platforms and principles

| Component | HIG slug | Developer docs |
|---|---|---|
| Design principles | `design-principles` | — |
| Designing for iOS | `designing-for-ios` | — |
| Designing for iPadOS | `designing-for-ipados` | — |
| Designing for macOS | `designing-for-macos` | — |
| Designing for watchOS | `designing-for-watchos` | — |
| Designing for visionOS | `designing-for-visionos` | — |
| Designing for tvOS | `designing-for-tvos` | — |

Four names that look like slugs return 404 `text/html`, so they are not in the map: `navigation-bars`,
`confirmation-dialogs`, `launch-screens` and `haptics`. Navigation bars live under Toolbars
(`toolbars`), confirmation dialogs under Action sheets (`action-sheets`), launch screens under
Launching (`launching`), and haptics under Playing haptics (`playing-haptics`).

## Principles

Each rule points to the page to fetch rather than restating it.

- **Native first.** Use a system component and system style before a custom one. A custom control
  is justified only when no native component does the job, and that justification is recorded (see
  the workflow section below).
- **System fonts and Dynamic Type.** Use text styles (`.font(.body)`, `.headline`), not fixed point
  sizes. Layouts survive the largest accessibility sizes. Page: `typography`.
- **Semantic colours.** Use system and semantic colours, and asset-catalog colours with a dark
  appearance, never literal RGB in a view. Pages: `color`, `dark-mode`.
- **SF Symbols** for iconography, through `Image(systemName:)` / `Label`. Page: `sf-symbols`.
- **Standard spacing.** Use the system's default padding, and the standard list and form insets,
  before literals. Page: `layout`.
- **Platform placement.** Put toolbar items in semantic placements (`ToolbarItemPlacement`:
  `.primaryAction`, `.confirmationAction`, `.cancellationAction`) before positional ones.
  Destructive actions carry `role: .destructive`. Use the standard Back and Close buttons. Pages:
  `toolbars`, `buttons`.
- **Accessibility is part of the component.** Every control has a label VoiceOver reads, animation
  respects Reduce Motion, and meaning is never carried by colour alone. Pages: `accessibility`,
  `motion`.
- **API availability.** Before using an API, check `metadata.platforms` against the deployment
  target. An API newer than the target needs `if #available` with a fallback, and that is the
  project's call, so raise it. A deprecated API is not used in new code.

## At each step of a change

### Clarify

List the UI components the request touches and fetch their HIG pages (and the API pages where the
request names behaviour). **Raise every place where the request or a design handoff goes against
the guidelines, or replaces a native component with a custom one, as a step 0 question.** Each
question cites the page and offers the native alternative. Magnus decides. An approved deviation
goes into `brief.md` under `## Decisions taken` as `HIG deviation: <what> — <reason> (approved)`.

### Plan

Every UI decision gets a row in *Conventions applied* with source `HIG <slug>` or `SwiftUI <path>`.
Each approved deviation gets a row with source `deviation` and the reason from the brief. A plan
that adds a custom control states which native component it rejected, and why.

### Review

**Blocking** findings are a HIG deviation not approved in the brief or plan, a custom control where
a native one fits, a fixed font size or literal colour in a view, a control with no accessibility
label, and a deprecated API or one newer than the deployment target without a fallback. Cite the
page in the finding. A deviation recorded with a reason is not a finding.

## Rules

- **Fetch, do not recall.** The HIG changes, so cite the page you fetched, not your memory of it.
- **Never paste fetched guidance into the repo.**
- **Never add a slug to the map that you did not get a 200 for.**
- **The project's `CLAUDE.md` wins over everything here.**
