"""Profiles — create, remove, edit, list."""

from __future__ import annotations

import os
import subprocess

from sm_cli import core


def add(
    name: str,
    skills: list[str] | None = None,
    desc: str = "",
    force: bool = False,
) -> None:
    core.ensure_initialized()
    existed = core.profile_exists(name)
    if existed and not force:
        raise SystemExit(f"Profile '{name}' exists. Use --force to overwrite.")
    core.save_profile(name, {
        "name": name,
        "description": desc,
        "skills": skills or [],
    })
    print(f"✓ Profile '{name}' {'updated' if existed else 'created'}.")


def remove(name: str) -> None:
    core.ensure_initialized()
    p = core.profile_path(name)
    if not p.exists():
        raise SystemExit(f"Profile '{name}' not found.")
    p.unlink()
    print(f"✓ Profile '{name}' removed.")


def edit(name: str) -> None:
    core.ensure_initialized()
    p = core.profile_path(name)
    if not p.exists():
        raise SystemExit(f"Profile '{name}' not found. Use `sm add {name}` first.")
    editor = os.environ.get("EDITOR", "vim")
    print(f"Opening {p} in {editor} …")
    subprocess.run([editor, str(p)])


def list_all() -> None:
    core.ensure_initialized()
    names = core.list_profiles()
    if not names:
        print("No profiles.")
        return
    for name in names:
        p = core.load_profile(name)
        skills = p.get("skills", [])
        desc = p.get("description", "")
        print(f"  {name}:")
        if desc:
            print(f"    description: {desc}")
        print(f"    skills: {', '.join(skills) if skills else '(none)'}")
