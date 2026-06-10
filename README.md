# sm — Agent Skill Manager

<p align="center">
<b>One skill set, many agents.</b><br>
<sup>Deploy the same skills to Claude Code · Codex · Pi · Cursor via symlinks.</sup>
</p>

---

```
$ sm skills add anthropics/skills -l

╭──────────────────────────────────────────────────────────────╮
│ anthropics/skills                                            │
├──────────────────────┬──────────────────────────────────────┤
│ Skill                │ Description                          │
├──────────────────────┼──────────────────────────────────────┤
│ pdf                  │ Use this skill whenever the user    │
│                      │ wants to do anything with PDF files │
├──────────────────────┼──────────────────────────────────────┤
│ docx                 │ Use this skill whenever the user    │
│                      │ wants to create, read, or edit     │
│                      │ Word documents                      │
├──────────────────────┼──────────────────────────────────────┤
│ ...                  │ 15 more                             │
╰──────────────────────┴──────────────────────────────────────╯

$ sm skills add anthropics/skills -s pdf docx
✓ Installed 2 skill(s): pdf, docx

$ sm add work --skills pdf,docx,deep-research --desc "Daily work"
✓ Profile 'work' created.

$ sm use work claude
Deploying 'work' → claude (global) …
  ✓ 3 skill(s) linked
Launching claude …
```

## Install

```bash
uv tool install .
# or from git
uv tool install git+https://github.com/ayotme/skill-manager
```

## Commands

```
sm status                            Show status

sm skills add <owner/repo|url|path>  Install skill(s)
  [-s pdf] [-l]
sm skills list                       List installed skills
sm skills remove <name>              Remove a skill
sm skills update [name]              Update from source

sm add <name> [--skills a,b]         Create a profile
  [--desc text] [--force]
sm list                              List profiles
sm remove <name>                     Delete a profile
sm edit <name>                       Edit in $EDITOR

sm use <profile> <agent>             Deploy + launch
sm use <profile> <agent> -p          Project-local
sm unuse <profile> <agent>           Remove deployment
```

## Custom Agents

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

## How It Works

```
~/.sm/
  repos/               Git clones (single source of truth)
  skills/              Symlinks → repos/ or local paths
  profiles/            Profile configs (JSON)
  agents.json          Custom agents (optional)
```

`sm use` creates symlinks from `~/.sm/skills/` into the agent's skill directory. Switching profiles swaps the links. Zero magic, just symlinks.

## License

MIT
