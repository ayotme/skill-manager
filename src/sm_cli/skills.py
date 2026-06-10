"""Skills — install, remove, update, list."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

from sm_cli import core


def add(source: str, skill: str | None = None, list_only: bool = False) -> None:
    core.ensure_initialized()
    # expand owner/repo short format
    if "/" in source and not source.startswith(("https://", "git@", "git+", "/")):
        source = f"https://github.com/{source}"
    if source.startswith(("https://", "git@", "git+")):
        _add_git(source, skill, list_only)
    elif Path(source).is_dir():
        if list_only:
            raise SystemExit("--list is only supported for git repos.")
        _add_local(source, skill)
    else:
        raise SystemExit(f"Unknown source: {source}")


def remove(name: str) -> None:
    core.ensure_initialized()
    p = core.skills_dir() / name
    if not p.exists():
        raise SystemExit(f"'{name}' not found.")
    if p.is_symlink():
        p.unlink()
    else:
        shutil.rmtree(p)
    print(f"✓ '{name}' removed.")


def update(name: str | None = None) -> None:
    core.ensure_initialized()
    repos = core.repos_dir()
    if not repos.exists():
        print("No git skills installed.")
        return

    repo_names = sorted(
        d.name for d in repos.iterdir()
        if d.is_dir() and (d / ".source.json").exists()
    )

    # filter by skill name if specified
    if name:
        skill_link = core.skills_dir() / name
        if not skill_link.exists():
            raise SystemExit(f"Skill '{name}' not found.")
        if skill_link.is_symlink():
            target = os.readlink(skill_link)
            repos_str = str(repos) + "/"
            if target.startswith(repos_str):
                repo_name = target[len(repos_str):].split("/")[0]
                repo_names = [repo_name]
            else:
                print(f"  {name}: skipped (not from git)")
                return
        else:
            print(f"  {name}: skipped (not a symlink)")
            return

    updated = 0
    for repo_name in repo_names:
        repo_path = repos / repo_name
        src = core.load_json(repo_path / ".source.json")
        url = src.get("url")
        if not url:
            continue

        print(f"  Updating {repo_name} …")
        shutil.rmtree(repo_path)
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp) / repo_name
            r = subprocess.run(
                ["git", "clone", "--depth", "1", url, str(tmp_path)],
                capture_output=True, text=True,
            )
            if r.returncode != 0:
                print(f"    Failed: {r.stderr.strip()}")
                continue
            shutil.move(str(tmp_path), str(repo_path))

        core.save_json(repo_path / ".source.json", {
            **src, "updated_at": datetime.now().isoformat(),
        })

        # re-link skills from this repo
        for skill_name, skill_path in core.scan_skill_dirs(repo_path):
            link = core.skills_dir() / skill_name
            if link.is_symlink():
                link.unlink()
                link.symlink_to(skill_path)

        print("    ✓")
        updated += 1

    print(f"\n✓ Updated {updated}/{len(repo_names)} repo(s)")


def _skill_source(skill_path: Path) -> str:
    """Return 'git' or 'local' based on where the symlink points."""
    if skill_path.is_symlink():
        target = os.readlink(skill_path)
        if target.startswith(str(core.repos_dir())):
            return "git"
    return "local"


def list_installed() -> None:
    core.ensure_initialized()
    names = core.list_skills()
    if not names:
        print("No skills installed.")
        return
    for name in names:
        skill_path = core.skills_dir() / name
        src = _skill_source(skill_path)
        desc = _read_description(skill_path / "SKILL.md")
        line = f"  {name} ({src})"
        if desc:
            line += f"  — {desc}"
        print(line)


# ── internal ─────────────────────────────────────────────────────────────


def _add_git(url: str, skill: str | None = None, list_only: bool = False) -> None:
    repo_name = url.rstrip("/").split("/")[-1].removesuffix(".git")
    repo_path = core.repos_dir() / repo_name

    core.repos_dir().mkdir(parents=True, exist_ok=True)
    if repo_path.exists():
        print(f"Updating cached repo '{repo_name}' …")
        shutil.rmtree(repo_path)

    print(f"Cloning {url} …")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp) / repo_name
        r = subprocess.run(
            ["git", "clone", "--depth", "1", url, str(tmp_path)],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            raise SystemExit(f"Clone failed:\n{r.stderr}")
        shutil.move(str(tmp_path), str(repo_path))

    # scan for skill directories
    all_skills = core.scan_skill_dirs(repo_path)
    if not all_skills:
        shutil.rmtree(repo_path)
        raise SystemExit(f"No skills found in {url} (no SKILL.md detected).")

    # --list: just show and exit
    if list_only:
        print(f"Skills in {url} ({len(all_skills)}):\n")
        for skill_name, skill_path in all_skills:
            desc = _read_description(skill_path / "SKILL.md")
            line = f"  {skill_name}"
            if desc:
                line += f"  — {desc}"
            print(line)
        shutil.rmtree(repo_path)
        return

    # record source
    core.save_json(repo_path / ".source.json", {
        "type": "git", "url": url,
        "installed_at": datetime.now().isoformat(),
    })

    # apply --skill filter
    if skill:
        filtered = [(n, p) for n, p in all_skills if n == skill]
        if not filtered:
            avail = ", ".join(n for n, _ in all_skills)
            raise SystemExit(f"Skill '{skill}' not found. Available: {avail}")
        all_skills = filtered

    # symlink each skill
    core.skills_dir().mkdir(parents=True, exist_ok=True)
    installed = []
    for skill_name, skill_path in all_skills:
        if not skill_path.exists():
            print(f"  Warning: '{skill_name}' path missing after clone, skipping.")
            continue
        link = core.skills_dir() / skill_name
        if link.exists():
            print(f"  Skipped '{skill_name}' (already exists).")
            continue
        link.symlink_to(skill_path)
        installed.append(skill_name)

    if installed:
        print(f"✓ Installed {len(installed)} skill(s): {', '.join(installed)}")
    else:
        print("No new skills installed (all already exist).")


def _add_local(path: str, skill: str | None = None) -> None:
    src = Path(path).resolve()
    if not src.is_dir():
        raise SystemExit(f"Not a directory: {path}")
    if not skill:
        skill = src.name
    target = core.skills_dir() / skill
    if target.exists():
        raise SystemExit(f"'{skill}' already exists.")
    target.symlink_to(src)
    core.save_json(target / ".source.json", {
        "type": "local", "path": str(src),
        "installed_at": datetime.now().isoformat(),
    })
    print(f"✓ '{skill}' linked from {src}")


def _read_description(skill_file: Path) -> str:
    """Extract description from SKILL.md YAML frontmatter."""
    try:
        text = skill_file.read_text()
        if text.startswith("---"):
            end = text.find("---", 3)
            if end != -1:
                for line in text[3:end].splitlines():
                    if line.startswith("description:"):
                        return line.split(":", 1)[1].strip().strip("\"'")
    except OSError:
        pass
    return ""
