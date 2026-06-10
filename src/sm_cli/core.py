"""Core — paths, JSON helpers, agent config, auto-init."""

from __future__ import annotations

import json
import os
from importlib import resources
from pathlib import Path
from typing import Any

SM_HOME = Path(os.environ.get("SM_HOME", str(Path.home() / ".sm")))


# ── paths ────────────────────────────────────────────────────────────────


def skills_dir() -> Path:
    return SM_HOME / "skills"


def profiles_dir() -> Path:
    return SM_HOME / "profiles"


def repos_dir() -> Path:
    return SM_HOME / "repos"


def profile_path(name: str) -> Path:
    return profiles_dir() / f"{name}.json"


# ── JSON ─────────────────────────────────────────────────────────────────


def load_json(path: Path) -> dict[str, Any]:
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def save_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


# ── agents ───────────────────────────────────────────────────────────────


def load_agents() -> dict[str, Any]:
    """Merge built-in + user agents. User overrides take precedence."""
    ref = resources.files("sm_cli").joinpath("agents.json")
    with resources.as_file(ref) as p:
        with open(p) as f:
            agents = json.load(f)
    agents.update(load_json(SM_HOME / "agents.json"))
    return agents


def agent_names() -> list[str]:
    return list(load_agents().keys())


def get_agent(name: str) -> dict[str, str]:
    agents = load_agents()
    if name not in agents:
        raise SystemExit(f"Unknown agent '{name}'. Supported: {', '.join(agents)}")
    return agents[name]


def resolve_target(agent_name: str, project: bool = False) -> Path:
    agent = get_agent(agent_name)
    key = "project" if project else "global"
    raw = agent[key]
    if project:
        return Path.cwd() / raw
    return Path(raw.replace("~", str(Path.home())))


# ── profiles ─────────────────────────────────────────────────────────────


def load_profile(name: str) -> dict[str, Any]:
    p = profile_path(name)
    if not p.exists():
        raise SystemExit(f"Profile '{name}' not found.")
    return load_json(p)


def save_profile(name: str, data: dict[str, Any]) -> None:
    save_json(profile_path(name), data)


def list_profiles() -> list[str]:
    d = profiles_dir()
    if not d.exists():
        return []
    return sorted(f.stem for f in d.iterdir() if f.suffix == ".json")


def profile_exists(name: str) -> bool:
    return profile_path(name).exists()


# ── skills ───────────────────────────────────────────────────────────────


def list_skills() -> list[str]:
    d = skills_dir()
    if not d.exists():
        return []
    return sorted(p.name for p in d.iterdir() if p.is_dir())


def scan_skill_dirs(repo_path: Path) -> list[tuple[str, Path]]:
    """Recursively find all directories containing SKILL.md."""
    return [
        (f.parent.name, f.parent)
        for f in sorted(repo_path.rglob("SKILL.md"))
    ]


# ── auto-init ────────────────────────────────────────────────────────────


def ensure_initialized() -> None:
    if not profiles_dir().exists():
        skills_dir().mkdir(parents=True, exist_ok=True)
        repos_dir().mkdir(parents=True, exist_ok=True)
        profiles_dir().mkdir(parents=True, exist_ok=True)
