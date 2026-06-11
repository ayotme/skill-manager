"""sm — Skill Manager. Entry point and dispatch."""

from __future__ import annotations

import os
import sys

from sm_cli import core
from sm_cli import deploy
from sm_cli import display
from sm_cli import profiles
from sm_cli import skills


# ── use / unuse ─────────────────────────────────────────────────────────


def use_profile(profile_name: str, agent: str, project: bool = False) -> None:
    core.ensure_initialized()
    mode = "project" if project else "global"
    print(f"Deploying '{profile_name}' → {agent} ({mode}) …")
    count = deploy.deploy(profile_name, agent, project=project)
    print(f"  ✓ {count} skill(s) linked")
    cmd = core.get_agent(agent)["command"]
    print(f"Launching {cmd} …")
    os.execvp(cmd, [cmd])


def unuse_profile(profile_name: str, agent: str, project: bool = False) -> None:
    core.ensure_initialized()
    mode = "project" if project else "global"
    removed = deploy.undeploy(profile_name, agent, project=project)
    print(f"✓ Removed {removed} skill(s) from {agent} ({mode})")


# ── status ───────────────────────────────────────────────────────────────


def show_status() -> None:
    core.ensure_initialized()
    display.status(
        home=str(core.SM_HOME),
        agents=core.agent_names(),
        skill_names=core.list_skills(),
        profile_names=core.list_profiles(),
    )


# ── help ─────────────────────────────────────────────────────────────────

HELP = """\
sm — Skill Manager

Skills (first-class):
  sm add <owner/repo|url|path>           Install skill(s)
    [-s pdf,docx] [-l]
  sm ls                                  List installed skills
  sm rm [name]                           Remove a skill (omit for all)
  sm update [name]                       Update skill(s) from source

Profiles:
  sm profile add <name> --skills ...     Create a profile
    [--desc text] [--force]
  sm profile ls                          List profiles
  sm profile edit <name>                 Edit in $EDITOR
  sm profile rm <name>                   Remove a profile

Deploy:
  sm use <profile> <agent>               Deploy + launch (global)
  sm use <profile> <agent> -p            Deploy + launch (project-local)
  sm unuse <profile> <agent>             Remove deployment

Agents: claude, codex, pi, cursor
  (configurable in ~/.sm/agents.json)

Examples:
  sm add anthropics/skills                     # install all
  sm add anthropics/skills -l                  # preview
  sm add anthropics/skills -s pdf,docx,pptx    # specific skills
  sm profile add work --skills pdf,docx --desc "Daily work"
  sm use work claude
"""


# ── main ─────────────────────────────────────────────────────────────────


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help", "help"):
        print(HELP)
        return

    cmd = args[0]

    if cmd == "status":
        show_status()
    elif cmd == "add":
        _dispatch_skill_add(args[1:])
    elif cmd in ("ls", "list"):
        skills.list_installed()
    elif cmd in ("rm", "remove"):
        name = args[1] if len(args) > 1 else None
        skills.remove(name)
    elif cmd == "update":
        skills.update(args[1] if len(args) > 1 else None)
    elif cmd == "profile":
        _dispatch_profile(args[1:])
    elif cmd == "use":
        _dispatch_use(args[1:], deploy_mode=True)
    elif cmd == "unuse":
        _dispatch_use(args[1:], deploy_mode=False)
    else:
        print(f"Unknown command: '{cmd}'")
        print("Run `sm --help` for usage.")
        raise SystemExit(1)


# ── dispatch: skills ─────────────────────────────────────────────────────


def _dispatch_skill_add(args: list[str]) -> None:
    if not args:
        raise SystemExit("Usage: sm add <owner/repo|url|path> [-s name] [-l]")
    source = args[0]
    skills_list: list[str] = []
    list_only = False
    i = 1
    while i < len(args):
        if args[i] in ("-s", "--skill") and i + 1 < len(args):
            skills_list.extend(
                s.strip() for s in args[i + 1].split(",") if s.strip()
            )
            i += 2
        elif args[i] in ("-l", "--list"):
            list_only = True
            i += 1
        else:
            i += 1
    sk = skills_list if skills_list else None
    skills.add(source, sk, list_only)


# ── dispatch: profile ────────────────────────────────────────────────────


def _dispatch_profile(args: list[str]) -> None:
    sub = args[0] if args else "ls"
    if sub in ("ls", "list"):
        profiles.list_all()
    elif sub == "add":
        _dispatch_profile_add(args[1:])
    elif sub in ("rm", "remove"):
        if len(args) < 2:
            raise SystemExit("Usage: sm profile rm <name>")
        profiles.remove(args[1])
    elif sub == "edit":
        if len(args) < 2:
            raise SystemExit("Usage: sm profile edit <name>")
        profiles.edit(args[1])
    else:
        raise SystemExit(f"Unknown: sm profile {sub}")


def _dispatch_profile_add(args: list[str]) -> None:
    if not args:
        raise SystemExit("Usage: sm profile add <name> --skills ... [--desc text] [--force]")
    name = args[0]
    sk: list[str] | None = None
    desc = ""
    force = False
    i = 1
    while i < len(args):
        if args[i] == "--skills" and i + 1 < len(args):
            sk = [s.strip() for s in args[i + 1].split(",") if s.strip()]
            i += 2
        elif args[i] == "--desc" and i + 1 < len(args):
            desc = args[i + 1]
            i += 2
        elif args[i] == "--force" or args[i] == "-f":
            force = True
            i += 1
        else:
            i += 1
    profiles.add(name, sk, desc, force)


# ── dispatch: use / unuse ────────────────────────────────────────────────


def _dispatch_use(args: list[str], *, deploy_mode: bool) -> None:
    rest, project = _parse_project(args)
    cmd = "use" if deploy_mode else "unuse"
    if len(rest) < 2:
        raise SystemExit(f"Usage: sm {cmd} <profile> <agent> [-p]")
    profile_name, agent = rest[0], rest[1]
    if deploy_mode:
        use_profile(profile_name, agent, project=project)
    else:
        unuse_profile(profile_name, agent, project=project)


def _parse_project(args: list[str]) -> tuple[list[str], bool]:
    project = False
    rest = []
    for a in args:
        if a in ("-p", "--project"):
            project = True
        else:
            rest.append(a)
    return rest, project
