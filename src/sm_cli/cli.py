"""sm — Agent Skill Manager. Entry point and dispatch."""

from __future__ import annotations

import os
import sys

from . import core
from . import deploy
from . import profiles
from . import skills


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
    agents = core.agent_names()
    sk = core.list_skills()
    pr = core.list_profiles()
    print(f"Skill Manager  {core.SM_HOME}")
    print(f"Agents: {', '.join(agents)}")
    print(f"Skills: {len(sk)}   Profiles: {len(pr)}")


# ── help ─────────────────────────────────────────────────────────────────

HELP = """\
sm — Agent Skill Manager

Usage:
  sm status                              Show current status

Profile management:
  sm add <name> [--skills a,b,c]         Create a profile
    [--desc text] [--force]
  sm list                                List all profiles
  sm remove <name>                       Remove a profile
  sm edit <name>                         Edit profile in $EDITOR

Skills:
  sm skills add <url|path|owner/repo>    Install skill(s)
    [-s, --skill name] [-l, --list]
  sm skills list                         List installed skills
  sm skills remove <name>                Remove a skill
  sm skills update [name]                Update skill(s) from source

Deploy:
  sm use <profile> <agent>               Deploy + launch agent (global)
  sm use <profile> <agent> -p            Deploy + launch agent (project-local)
  sm unuse <profile> <agent>             Remove deployed skill links (global)
  sm unuse <profile> <agent> -p          Remove deployed skill links (project-local)

Agents: claude, codex, pi, cursor
  (configurable in ~/.sm/agents.json)

Examples:
  sm skills add anthropics/skills              # short format
  sm skills add anthropics/skills -l           # list before installing
  sm skills add anthropics/skills -s pdf       # install specific skill
  sm add work --skills pdf,docx,deep-research
  sm use work claude
  sm use work claude -p
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
    elif cmd == "skills":
        _dispatch_skills(args[1:])
    elif cmd == "add":
        _dispatch_add(args[1:])
    elif cmd == "list":
        profiles.list_all()
    elif cmd == "remove":
        if len(args) < 2:
            raise SystemExit("Usage: sm remove <profile>")
        profiles.remove(args[1])
    elif cmd == "edit":
        if len(args) < 2:
            raise SystemExit("Usage: sm edit <profile>")
        profiles.edit(args[1])
    elif cmd == "use":
        _dispatch_use(args[1:], deploy_mode=True)
    elif cmd == "unuse":
        _dispatch_use(args[1:], deploy_mode=False)
    else:
        print(f"Unknown command: '{cmd}'")
        print("Run `sm --help` for usage.")
        raise SystemExit(1)


# ── dispatch ─────────────────────────────────────────────────────────────


def _dispatch_skills(args: list[str]) -> None:
    sub = args[0] if args else "list"
    if sub == "list":
        skills.list_installed()
    elif sub == "add":
        if len(args) < 2:
            raise SystemExit("Usage: sm skills add <url|path|owner/repo> [-s name] [-l]")
        source = args[1]
        sk = None
        list_only = False
        i = 2
        while i < len(args):
            if args[i] in ("-s", "--skill") and i + 1 < len(args):
                sk = args[i + 1]
                i += 2
            elif args[i] in ("-l", "--list"):
                list_only = True
                i += 1
            else:
                i += 1
        skills.add(source, sk, list_only)
    elif sub == "remove":
        if len(args) < 2:
            raise SystemExit("Usage: sm skills remove <name>")
        skills.remove(args[1])
    elif sub == "update":
        skills.update(args[1] if len(args) > 1 else None)
    else:
        raise SystemExit(f"Unknown: sm skills {sub}")


def _dispatch_add(args: list[str]) -> None:
    if not args:
        raise SystemExit("Usage: sm add <name> [--skills a,b,c] [--desc text] [--force]")
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
