# sm — Lightweight Agent Skill Manager

One skill set, many agents. Deploy the same skills to different AI coding agents via symlinks.

**Zero config.** Just install and go.

```bash
# Install
uv tool install .
```

## Quick Start

```bash
# Install skills from GitHub (auto-scans for SKILL.md)
sm skills add anthropics/skills

# Preview what's in a repo before installing
sm skills add anthropics/skills -l

# Install a specific skill from a multi-skill repo
sm skills add anthropics/skills -s pdf

# Install from a local directory
sm skills add /path/to/my-skill

# Create a profile — a named set of skills
sm add default --skills pdf,docx,deep-research --desc "Daily development"

# Deploy to an agent and launch
sm use default claude       # global deploy + launch Claude Code
sm use default claude -p    # project-local deploy + launch

# Remove deployment
sm unuse default claude
```

## Commands

```
sm status                              Show status

sm skills add <url|path|owner/repo>    Install skill(s)
  [-s, --skill name] [-l, --list]
sm skills list                         List installed skills
sm skills remove <name>                Remove a skill
sm skills update [name]                Update skill(s) from source

sm add <name> [--skills a,b,c]         Create a profile
  [--desc text] [--force]
sm list                                List all profiles
sm remove <name>                       Remove a profile
sm edit <name>                         Edit profile in $EDITOR

sm use <profile> <agent>               Deploy + launch (global)
sm use <profile> <agent> -p            Deploy + launch (project-local)
sm unuse <profile> <agent>             Remove deployment
```

## How It Works

```
~/.sm/repos/anthropics-skills/       ← git clone (single source of truth)
~/.sm/skills/
  pdf    → repos/anthropics-skills/skills/pdf/     ← symlink
  docx   → repos/anthropics-skills/skills/docx/
  deep-research → /path/to/local/deep-research/    ← local link

sm use docs claude
  ↓
~/.claude/skills/
  pdf           → ~/.sm/skills/pdf/
  docx          → ~/.sm/skills/docx/
  deep-research → ~/.sm/skills/deep-research/
```

Each skill is a directory containing a `SKILL.md`. The manager symlinks them into the agent's skill location. Switching profiles automatically replaces the links.

### Multi-skill Repos

GitHub repos often contain multiple skills. `sm skills add` automatically scans the repo for all directories containing `SKILL.md` and installs each one individually:

```bash
# Installs all 18 skills from the repo
sm skills add anthropics/skills

# Preview what's available before installing
sm skills add anthropics/skills -l

# Install just one
sm skills add anthropics/skills -s pdf
```

### Updates

Skills installed from git are stored as symlinks into the cloned repo. Updating is a single re-clone:

```bash
sm skills update       # update all git repos
sm skills update pdf   # update the repo containing pdf
```

## Built-in Agents

| Agent | Global | Project | Command |
|-------|--------|---------|---------|
| Claude Code | `~/.claude/skills/` | `.claude/skills/` | `claude` |
| Codex | `~/.codex/skills/` | `.codex/skills/` | `codex` |
| Pi | `~/.pi/agent/skills/` | `.pi/skills/` | `pi` |
| Cursor | `~/.cursor/skills/` | `.cursor/skills/` | `cursor` |

## Adding Custom Agents

Create `~/.sm/agents.json`:

```json
{
  "windsurf": {
    "command": "windsurf",
    "global": "~/.windsurf/skills",
    "project": ".windsurf/skills"
  }
}
```

User config is merged with built-in defaults. Matching keys override the defaults.

## Global vs Project-local

- **Global** `sm use <profile> <agent>` — deploys to `~/<agent-path>/skills/`, applies everywhere
- **Project-local** `sm use <profile> <agent> -p` — deploys to `./<agent-path>/skills/`, current directory only

Both can coexist independently.

## Data Location

```
~/.sm/
  repos/               Git clones (source of truth for git skills)
  skills/              Skill directories (symlinks to repos/ or local paths)
  profiles/            Profile configs (JSON)
  agents.json          Custom agent overrides (optional)
```

Set `SM_HOME` environment variable to change the base path.
