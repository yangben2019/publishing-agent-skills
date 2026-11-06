#!/usr/bin/env python3
"""Validate an agent-skill repository before publishing.

Usage:
    python validate.py <repo-or-skills-dir> [<another> ...]

Checks the things that decide whether the skills CLI can find the skill and
whether the model will ever trigger it:
  - a discoverable SKILL.md under a recognised container
  - YAML frontmatter with `name` and `description`
  - name: lowercase kebab-case, <= 64 chars, matches its folder
  - description: <= 1024 chars, third person, contains a "use when" clause
  - body: non-trivial but under the 500-line guideline
  - plugin manifests parse as JSON
  - README and LICENSE exist at the repo root

Exit code 0 = no errors (warnings allowed), 1 = errors.
"""

import json
import re
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
FORBIDDEN = ("anthropic", "claude")
CONTAINERS = ("skills", ".claude/skills", ".agents/skills")

errors, warnings, seen = [], [], {}


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def parse_frontmatter(text):
    if not text.startswith("---"):
        return None, None
    end = text.find("\n---", 3)
    if end == -1:
        return None, None
    data = {}
    for line in text[3:end].splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        m = re.match(r"^([A-Za-z_][\w.-]*):\s*(.*)$", line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "'\"":
            val = val[1:-1]
        data[key] = val
    return data, text[end + 4:]


def find_skills(root):
    found = []
    for container in CONTAINERS:
        base = root / container
        if not base.is_dir():
            continue
        for path in base.rglob("SKILL.md"):
            depth = len(path.relative_to(base).parts)
            if depth <= 3:
                found.append(path)
    return sorted(set(found))


def check_skill(path):
    label = str(path)
    fm, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    if fm is None:
        err(f"{label}: frontmatter missing or not closed")
        return

    name, desc = fm.get("name"), fm.get("description")

    if not name:
        err(f"{label}: missing 'name'")
    else:
        if not NAME_RE.match(name):
            err(f"{label}: name '{name}' is not lowercase kebab-case")
        if len(name) > 64:
            err(f"{label}: name is {len(name)} chars (max 64)")
        if name != path.parent.name:
            err(f"{label}: name '{name}' != folder '{path.parent.name}'")
        for bad in FORBIDDEN:
            if bad in name:
                err(f"{label}: name must not contain '{bad}'")
        if name in seen:
            err(f"{label}: duplicate name, also at {seen[name]}")
        else:
            seen[name] = label

    if not desc:
        err(f"{label}: missing 'description'")
    else:
        if len(desc) > 1024:
            err(f"{label}: description is {len(desc)} chars (max 1024)")
        if len(desc) < 120:
            warn(f"{label}: description is short ({len(desc)} chars) — may under-trigger")
        if not re.search(r"\b(use when|use this|prefer this)\b", desc, re.I):
            warn(f"{label}: description has no 'Use when ...' clause")
        if re.match(r"^(I|We)\b", desc):
            err(f"{label}: description should be third person")

    lines = (body or "").splitlines()
    if len(lines) < 20:
        warn(f"{label}: body is only {len(lines)} lines")
    if len(lines) > 500:
        warn(f"{label}: body is {len(lines)} lines (guideline: < 500)")


def check_repo(root):
    for manifest in ("marketplace.json", "plugin.json"):
        path = root / ".claude-plugin" / manifest
        if path.exists():
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:
                err(f"{root.name}: invalid JSON in {manifest} — {exc}")

    for required in ("README.md", "LICENSE"):
        if not (root / required).exists():
            err(f"{root.name}: missing {required}")

    skills = find_skills(root)
    if not skills:
        err(f"{root.name}: no SKILL.md found under {', '.join(CONTAINERS)}")
        return
    for skill in skills:
        check_skill(skill)


def main(argv):
    targets = [Path(a).resolve() for a in argv[1:]]
    if not targets:
        print(__doc__)
        return 1

    for target in targets:
        if (target / "skills").is_dir() or (target / ".claude-plugin").is_dir():
            roots = [target]
        else:
            # Treat the target as a parent folder of repositories and skip
            # anything that is not one (scripts, notes, scratch dirs).
            roots = [
                p for p in target.iterdir()
                if p.is_dir() and ((p / "skills").is_dir() or (p / ".claude-plugin").is_dir())
            ]
        for root in roots:
            check_repo(root)

    print("=" * 60)
    print(f"Checked {len(seen)} skill(s) in {len(targets)} target(s)")
    print("=" * 60)
    if warnings:
        print(f"\nWARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"  ~ {w}")
    if errors:
        print(f"\nERRORS ({len(errors)}):")
        for e in errors:
            print(f"  x {e}")
        return 1
    print("\nAll structural checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
