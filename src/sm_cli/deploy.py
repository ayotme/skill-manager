"""Deploy — symlink skills to agent directories."""

from __future__ import annotations

import os
from pathlib import Path

from . import core


def _is_managed(link: Path) -> bool:
    """Check if a symlink was created by sm (target is under skills_dir)."""
    try:
        return os.readlink(link).startswith(str(core.skills_dir()))
    except OSError:
        return False


def deploy(profile_name: str, agent_name: str, project: bool = False) -> int:
    """Deploy a profile's skills to an agent's target directory.

    Removes old managed symlinks, then creates new ones.
    Returns number of skills linked.
    """
    target = core.resolve_target(agent_name, project)
    target.mkdir(parents=True, exist_ok=True)

    # clean old managed symlinks
    for child in target.iterdir():
        if child.is_symlink() and _is_managed(child):
            child.unlink()

    profile = core.load_profile(profile_name)
    skill_names: list[str] = profile.get("skills", [])

    count = 0
    for skill_name in skill_names:
        src = core.skills_dir() / skill_name
        if not src.exists():
            print(f"  Warning: skill '{skill_name}' not installed, skipping.")
            continue
        link = target / skill_name
        if link.is_symlink():
            link.unlink()
        elif link.exists():
            print(f"  Warning: '{link}' already exists (not a symlink), skipping.")
            continue
        link.symlink_to(src)
        count += 1

    return count


def undeploy(profile_name: str, agent_name: str, project: bool = False) -> int:
    """Remove symlinks for a profile's skills from an agent's target directory.

    Returns number of symlinks removed.
    """
    target = core.resolve_target(agent_name, project)
    if not target.exists():
        return 0

    profile = core.load_profile(profile_name)
    skill_names: list[str] = profile.get("skills", [])

    removed = 0
    for skill_name in skill_names:
        link = target / skill_name
        if link.is_symlink() and _is_managed(link):
            link.unlink()
            removed += 1

    # prune empty dir
    if target.is_dir() and not any(target.iterdir()):
        target.rmdir()

    return removed
