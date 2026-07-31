#!/usr/bin/env python3
"""
Fail when a changed skill did not bump the versions it needs.

Two independent schemes, neither derived from the other:

    .tessl-plugin/plugin.json  version  ->  Tessl registry
    SKILL.md  metadata.version          ->  skills.sh installs

Forgetting the first fails the Tessl publish — but only AFTER merge, on main,
once the change is already in. Forgetting the second fails nothing at all: the
publish succeeds and skills.sh installs quietly keep serving the old copy.
This moves both signals to the pull request.

A version-only change (bumping plugin.json to unblock a publish, with no edit
to the skill itself) is NOT a content change and requires nothing further —
otherwise the fix for a missed bump would itself demand another bump.

    python3 scripts/check-skill-versions.py <base-ref>
"""
import json
import re
import subprocess
import sys

VERSION_LINE = re.compile(r'^\s*"?version"?:\s*.*$', re.M)


def git(*args):
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def at(ref, path):
    """File contents at a ref, or None when it did not exist there."""
    return git("show", f"{ref}:{path}")


def without_version(text):
    """The file minus any version line, so we can ask 'did anything else move?'"""
    return VERSION_LINE.sub("", text or "")


def plugin_version(text):
    try:
        return json.loads(text).get("version")
    except Exception:
        return None


def frontmatter_version(text):
    m = re.search(r'^\s*version:\s*"?([^"\s]+)"?', text or "", re.M)
    return m.group(1) if m else None


def main(base):
    changed = (git("diff", "--name-only", base, "HEAD", "--", "skills/") or "").split()
    skills = sorted({p.split("/")[1] for p in changed if p.startswith("skills/")})
    if not skills:
        print("No skill directories changed.")
        return 0

    problems = []
    for name in skills:
        prefix = f"skills/{name}/"
        files = [p for p in changed if p.startswith(prefix)]
        plugin_path = f"{prefix}.tessl-plugin/plugin.json"
        skill_path = f"{prefix}SKILL.md"

        new_plugin = at("HEAD", plugin_path)
        if new_plugin is None:
            problems.append(f"{name}: {plugin_path} is missing")
            continue
        old_plugin = at(base, plugin_path)
        if old_plugin is None:
            print(f"✓ {name}: new skill, nothing to compare against")
            continue

        # Did anything change beyond the version lines themselves?
        content_changed = False
        skill_body_changed = False
        for f in files:
            old, new = at(base, f), at("HEAD", f)
            if old is None or new is None:
                content_changed = True
                if f != plugin_path:
                    skill_body_changed = True
                continue
            if without_version(old) != without_version(new):
                content_changed = True
                if f != plugin_path:
                    skill_body_changed = True

        if not content_changed:
            print(f"✓ {name}: version-only change, nothing further required")
            continue

        ov, nv = plugin_version(old_plugin), plugin_version(new_plugin)
        if ov == nv:
            problems.append(
                f"{name}: .tessl-plugin/plugin.json version is still {nv} — "
                f"Tessl refuses to publish over an existing version, so the "
                f"publish job will fail on main after this merges"
            )

        osv = nsv = None
        if skill_body_changed:
            osv = frontmatter_version(at(base, skill_path))
            nsv = frontmatter_version(at("HEAD", skill_path))
            if osv is not None and osv == nsv:
                problems.append(
                    f"{name}: SKILL.md metadata.version is still {nsv} — "
                    f"skills.sh installs will keep serving the old copy. "
                    f"Nothing else catches this; it fails silently"
                )

        if not any(p.startswith(f"{name}:") for p in problems):
            detail = f"plugin {ov} -> {nv}"
            if skill_body_changed:
                detail += f", skill {osv} -> {nsv}"
            print(f"✓ {name}: {detail}")

    if problems:
        print("\nChanged skills with un-bumped versions:\n", file=sys.stderr)
        for p in problems:
            print(f"  ✘ {p}", file=sys.stderr)
        print(
            "\nThe two schemes are separate number lines; bumping one does not\n"
            "move the other:\n"
            "  .tessl-plugin/plugin.json  ->  Tessl registry\n"
            "  SKILL.md metadata.version  ->  skills.sh installs\n",
            file=sys.stderr,
        )
        return 1

    print(f"\nAll {len(skills)} changed skill(s) carry the bumps they need.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
