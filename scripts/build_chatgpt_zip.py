#!/usr/bin/env python3
"""Build the ZIP the ChatGPT plugin directory takes, after checking it.

The directory reads the Agent Plugins layout: `plugin.json` and `mcp.json` at
the root, `skills/`, and the images the manifest names. This packs exactly
those (never the Grok files, the README or anything secret) and checks the
limits the portal enforces first, so a mistake shows up here rather than as
an upload finding:

    python3 scripts/build_chatgpt_zip.py

Limits are from https://developers.openai.com/plugins/deploy/submission and
https://developers.openai.com/plugins/deploy/submission-errors.
"""

import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATEGORIES = {
    "Productivity", "Creativity", "Developer Tools", "Business & Operations",
    "Data & Analytics", "Communication", "Education & Research", "Security",
    "Finance", "Healthcare", "Travel", "Entertainment", "Other",
}
FORBIDDEN_KEYS = {"clientSecret", "test_credentials", "reviewer_instructions", "apps", "hooks"}
MAX_IMAGE_BYTES = 5 * 1024 * 1024

problems: list[str] = []


def check(ok: bool, message: str) -> None:
    if not ok:
        problems.append(message)


def one_line(value: str, limit: int, label: str) -> None:
    check(isinstance(value, str) and value.strip() != "", f"{label} is required")
    check("\n" not in value, f"{label} must be one line")
    check(len(value) <= limit, f"{label} is {len(value)} characters; at most {limit}")


def https(value: str, label: str) -> None:
    check(isinstance(value, str) and value.startswith("https://"), f"{label} must be HTTPS")
    check(len(value) <= 1024, f"{label} is longer than 1024 characters")


def keys_in(node, path=""):
    if isinstance(node, dict):
        for key, value in node.items():
            yield key, f"{path}.{key}" if path else key
            yield from keys_in(value, f"{path}.{key}" if path else key)
    elif isinstance(node, list):
        for i, value in enumerate(node):
            yield from keys_in(value, f"{path}[{i}]")


def svg_is_square(path: Path) -> bool:
    text = path.read_text("utf8")
    box = re.search(r'viewBox="\s*[\d.]+\s+[\d.]+\s+([\d.]+)\s+([\d.]+)\s*"', text)
    return bool(box) and box.group(1) == box.group(2) and float(box.group(1)) >= 48


def main() -> int:
    manifest = json.loads((ROOT / "plugin.json").read_text("utf8"))
    mcp = json.loads((ROOT / "mcp.json").read_text("utf8"))
    files = {"plugin.json", "mcp.json"}

    check(manifest.get("$schema", "").startswith("https://agent-plugins.org/schemas/"), "plugin.json needs the Agent Plugins $schema")
    name = manifest.get("name", "")
    check(re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) is not None and len(name) <= 64, "name must be kebab-case, at most 64 characters")
    check(re.fullmatch(r"\d+\.\d+\.\d+", manifest.get("version", "")) is not None, "version must be semantic, e.g. 1.0.0")
    check(len(manifest.get("description", "")) <= 4000, "description is longer than 4000 characters")

    for doc, label in ((manifest, "plugin.json"), (mcp, "mcp.json")):
        for key, where in keys_in(doc):
            check(key not in FORBIDDEN_KEYS, f"{label}: {where} is not allowed in a submitted package")

    openai = manifest.get("extensions", {}).get("com.openai", {})
    ui = openai.get("interface", {})
    one_line(ui.get("displayName", ""), 30, "interface.displayName")
    one_line(ui.get("shortDescription", ""), 30, "interface.shortDescription")
    check(0 < len(ui.get("longDescription", "")) <= 4000, "interface.longDescription is required, at most 4000 characters")
    one_line(ui.get("developerName", ""), 80, "interface.developerName")
    check(ui.get("category") in CATEGORIES, f"interface.category must be one of {sorted(CATEGORIES)}")
    caps = ui.get("capabilities", [])
    check(len(caps) <= 20, "at most 20 capabilities")
    for cap in caps:
        one_line(cap, 120, f"capability {cap!r}")
    for field in ("websiteURL", "supportURL", "privacyPolicyURL", "termsOfServiceURL"):
        https(ui.get(field, ""), f"interface.{field}")
    prompts = ui.get("defaultPrompt", [])
    prompts = [prompts] if isinstance(prompts, str) else prompts
    check(len(prompts) <= 3, "at most 3 starter prompts")
    check(len({" ".join(p.split()).lower() for p in prompts}) == len(prompts), "starter prompts must be unique")
    for prompt in prompts:
        one_line(prompt, 128, f"starter prompt {prompt!r}")
        check("@" not in prompt, f"starter prompt {prompt!r} must not @mention a server")
    check("screenshots" not in ui, "screenshots are only allowed for plugins with custom UI")

    for field in ("logo", "logoDark", "composerIcon", "composerIconDark"):
        rel = ui.get(field)
        if not rel:
            check(field not in ("logo",), f"interface.{field} is required")
            continue
        check(rel.startswith("./"), f"interface.{field} must start with ./")
        path = ROOT / rel
        check(path.is_file(), f"interface.{field}: {rel} is missing")
        if path.is_file():
            check(path.stat().st_size <= MAX_IMAGE_BYTES, f"{rel} is larger than 5 MiB")
            if path.suffix == ".svg":
                check(svg_is_square(path), f"{rel} must have a square viewBox of at least 48")
            files.add(rel[2:])

    onboarding = openai.get("onboardingSkill")
    if onboarding:
        check((ROOT / onboarding).is_file(), f"onboardingSkill {onboarding} is missing")

    review = openai.get("review", {})
    cases = review.get("test_cases", {})
    positive, negative = cases.get("positive", []), cases.get("negative", [])
    check(len(positive) == 5, f"exactly 5 positive test cases, found {len(positive)}")
    check(len(negative) == 3, f"exactly 3 negative test cases, found {len(negative)}")
    for case in positive:
        for field in ("description", "prompt", "tools_triggered", "expected_behavior"):
            check(bool(case.get(field)), f"positive case {case.get('description')!r} needs {field}")
    for case in negative:
        for field in ("description", "prompt"):
            check(bool(case.get(field)), f"negative case needs {field}")

    for locale, text in openai.get("publication", {}).get("translations", {}).items():
        if text.get("subtitle") is not None:
            one_line(text["subtitle"], 30, f"translations.{locale}.subtitle")
        if text.get("description") is not None:
            check(len(text["description"]) <= 4000, f"translations.{locale}.description is too long")

    servers = mcp.get("mcpServers", {})
    check(len(servers) == 1, "plugin-level test cases need exactly one MCP server")
    for server_name, server in servers.items():
        check(server.get("type") == "streamable-http", f"{server_name}: type must be streamable-http")
        https(server.get("url", ""), f"{server_name}.url")
        check(not server.get("headers"), f"{server_name}: server headers are rejected in a public submission")
        auth = server.get("extensions", {}).get("com.openai", {}).get("auth", {})
        check(auth.get("type") in ("oauth", "mixed"), f"{server_name}: a signed-in server needs oauth auth")

    for skill in sorted((ROOT / "skills").glob("*/SKILL.md")):
        text = skill.read_text("utf8")
        front = re.match(r"---\n(.*?)\n---\n", text, re.S)
        check(front is not None, f"{skill.relative_to(ROOT)} needs YAML front matter")
        if front:
            name_line = re.search(r"^name:\s*(.+)$", front.group(1), re.M)
            check(bool(name_line) and name_line.group(1).strip() == skill.parent.name,
                  f"{skill.relative_to(ROOT)}: name must match its folder")
            check(re.search(r"^description:\s*\S", front.group(1), re.M) is not None,
                  f"{skill.relative_to(ROOT)} needs a description")
        files.add(str(skill.relative_to(ROOT)))

    if problems:
        for problem in problems:
            print(f"✗ {problem}")
        print(f"{len(problems)} problem(s); nothing was built.")
        return 1

    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    out = dist / f"{name}-{manifest['version']}.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as archive:
        for rel in sorted(files):
            archive.write(ROOT / rel, rel)
    print(f"✓ {out.relative_to(ROOT)}")
    for rel in sorted(files):
        print(f"  {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
