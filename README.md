# sm

<p align="center">
<h3>Skill Manager for AI Agents</h3>
<h5>One skill set, many agents — Claude Code · Codex · Pi</h5>
</p>

<p align="center">
<img src="demo.gif" width="600" />
</p>

## Install

```bash
uv tool install git+https://github.com/ayotme/skill-manager
```

## Commands

**Skills**

```bash
sm add anthropics/skills -l              # preview available skills
sm add anthropics/skills -s pdf,docx      # install specific skills
sm ls                                     # list installed
sm rm xlsx                                # remove one
sm rm                                     # remove all
sm update                                 # refresh from source
```

**Profiles**

```bash
sm profile add work --skills pdf,docx,pptx,xlsx --desc "daily work"
sm profile ls
sm profile edit work
sm profile rm work
```

**Deploy**

```bash
sm use work claude                        # deploy + launch
sm use work claude -p                     # project-local
sm unuse work claude
```

Built-in agents: **claude** · **codex** · **pi** · **cursor**

## Custom Agents

Add agents in `~/.sm/agents.json`:

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
  repos/          ← git clones (cached, fast reuse)
  skills/         ← symlinks → repos/ or local paths
  profiles/       ← profile configs (JSON)
  agents.json     ← custom agents (optional)
```

`sm use` symlinks skills into the agent's directory. Switching profiles swaps the links. Zero magic.

## License

MIT
