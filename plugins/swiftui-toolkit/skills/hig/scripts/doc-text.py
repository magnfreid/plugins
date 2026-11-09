"""Prints the readable text of a developer.apple.com documentation JSON page.

Usage: curl -s -g <url>.json | python3 -I doc-text.py
"""
import json
import sys

page = json.load(sys.stdin)
refs = page.get("references", {})


def inline(items):
    out = []
    for item in items or []:
        kind = item.get("type")
        if kind == "text":
            out.append(item["text"])
        elif kind == "codeVoice":
            out.append("`" + item["code"] + "`")
        elif kind == "reference":
            ref = refs.get(item["identifier"], {})
            out.append(item.get("overridingTitle") or ref.get("title") or item["identifier"])
        elif "inlineContent" in item:
            out.append(inline(item["inlineContent"]))
    return "".join(out)


def block(b, depth=0):
    kind = b.get("type")
    if kind == "heading":
        print("\n" + "#" * b.get("level", 2) + " " + b["text"])
    elif kind == "paragraph":
        print(inline(b.get("inlineContent")))
    elif kind in ("unorderedList", "orderedList"):
        for item in b.get("items", []):
            for child in item.get("content", []):
                print("  " * depth + "- ", end="")
                block(child, depth + 1)
    elif kind == "aside":
        print("> " + (b.get("name") or b.get("style", "Note")) + ":")
        for child in b.get("content", []):
            block(child, depth)
    elif kind == "codeListing":
        print("\n".join(b.get("code", [])))
    elif kind == "table":
        for row in b.get("rows", []):
            cells = [" ".join(inline(c.get("inlineContent")) for c in cell) for cell in row]
            print("| " + " | ".join(cells) + " |")
    else:
        for key in ("content", "items", "tabs", "columns"):
            for child in b.get(key, []) or []:
                if isinstance(child, dict):
                    block(child, depth)


meta = page.get("metadata", {})
print(meta.get("title", ""))
print(inline(page.get("abstract")))
for p in meta.get("platforms", []) or []:
    line = "platform: " + p.get("name", "") + " " + p.get("introducedAt", "?")
    if "deprecatedAt" in p or p.get("deprecated"):
        line += " -- deprecated " + p.get("deprecatedAt", "") + ": " + p.get("message", "")
    print(line)
for b in page.get("deprecationSummary", []) or []:
    print("DEPRECATED:", inline(b.get("inlineContent")))
for section in page.get("primaryContentSections", []):
    for b in section.get("content", []) or []:
        block(b)
for ts in page.get("topicSections", []) or []:
    print("\n## Topics" + (": " + ts["title"] if ts.get("title") else ""))
    for ident in ts.get("identifiers", []):
        ref = refs.get(ident, {})
        print("-", ref.get("title", ident), ref.get("url", ""))
