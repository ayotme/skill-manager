"""Display — rich formatting for all sm output."""

from __future__ import annotations

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.box import ROUNDED

console = Console()


def skills_list(skills: list[dict]) -> None:
    """Display installed skills.

    Each item: {"name": str, "source": "git"|"local", "description": str}
    """
    if not skills:
        console.print("[dim]No skills installed.[/dim]")
        return

    table = Table(show_header=True, header_style="bold", box=ROUNDED, padding=(0, 1))
    table.add_column("Skill", style="cyan bold", min_width=16, vertical="middle")
    table.add_column("Source", style="dim", min_width=6, vertical="middle")
    table.add_column("Description", no_wrap=False)

    for s in skills:
        src_tag = "[green]git[/green]" if s["source"] == "git" else "[yellow]local[/yellow]"
        desc = s.get("description") or "[dim]-[/dim]"
        table.add_row(s["name"], src_tag, desc, end_section=True)

    console.print(table)


def profiles_list(profiles: list[dict]) -> None:
    """Display profiles.

    Each item: {"name": str, "description": str, "skills": list[str]}
    """
    if not profiles:
        console.print("[dim]No profiles.[/dim]")
        return

    table = Table(show_header=True, header_style="bold", box=ROUNDED, padding=(0, 1))
    table.add_column("Profile", style="cyan bold", min_width=16)
    table.add_column("Skills", min_width=20)
    table.add_column("Description")

    for p in profiles:
        skills = ", ".join(p.get("skills", [])) or "[dim]—[/dim]"
        desc = p.get("description", "[dim]—[/dim]")
        table.add_row(p["name"], skills, desc)

    console.print(table)


def repo_preview(url: str, skills: list[dict]) -> None:
    """Display skills found in a remote repo (--list).

    Each item: {"name": str, "description": str}
    """
    table = Table(
        title=f"[bold]{url}[/bold]",
        show_header=True,
        header_style="bold",
        box=ROUNDED,
        padding=(0, 1),
    )
    table.add_column("Skill", style="cyan bold", min_width=20)
    table.add_column("Description")

    for s in skills:
        desc = s.get("description", "[dim]—[/dim]")
        table.add_row(s["name"], desc)

    console.print()
    console.print(table)
    console.print(f"\n  [dim]{len(skills)} skill(s) found[/dim]")


def status(home: str, agents: list[str], n_skills: int, n_profiles: int) -> None:
    console.print(
        Panel(
            f"[bold]Home:[/bold]       {home}\n"
            f"[bold]Agents:[/bold]      {', '.join(agents)}\n"
            f"[bold]Skills:[/bold]      {n_skills}  [dim](use [bold]sm skills list[/bold] to see details)[/dim]\n"
            f"[bold]Profiles:[/bold]    {n_profiles}  [dim](use [bold]sm list[/bold] to see details)[/dim]",
            title="[bold]Skill Manager[/bold]",
            border_style="dim",
        )
    )
