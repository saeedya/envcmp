"""CLI entry point for piped."""

import typer
import piped.config as config
from rich.console import Console
from rich.table import Table

from piped.differ import diff
from piped.providers.base import BaseProvider
from piped.providers.env_file import EnvFileProvider
from piped.providers.gitlab import GitLabProvider
from piped.providers.github import GitHubProvider
from piped.providers.terraform import TerraformProvider

app = typer.Typer(help="Sync CI/CD variables between platforms.")
console = Console()


@app.command()
def diff_cmd(
    from_: str = typer.Option(..., "--from", help="Source provider (e.g. gitlab:my-project)"),
    to: str = typer.Option(..., "--to", help="Target provider (e.g. terraform:my-workspace)"),
) -> None:
    """Show differences between two providers."""
    source_provider = resolve_provider(from_)
    target_provider = resolve_provider(to)

    result = diff(source_provider, target_provider)

    if result.is_clean:
        console.print("[green]✓ Everything is in sync.[/green]")
        raise typer.Exit(0)

    table = Table(title="Diff Result")
    table.add_column("Key")
    table.add_column("Source")
    table.add_column("Target")
    table.add_column("Status")

    for var in result.in_sync:
        table.add_row(var.key, var.masked_value(), var.masked_value(), "[green]in sync[/green]")

    for var in result.source_only:
        table.add_row(var.key, var.masked_value(), "(not set)", "[yellow]source only[/yellow]")

    for var in result.target_only:
        table.add_row(var.key, "(not set)", var.masked_value(), "[yellow]target only[/yellow]")

    for source_var, target_var in result.differs:
        table.add_row(
            source_var.key,
            source_var.masked_value(),
            target_var.masked_value(),
            "[red]differs[/red]",
        )

    console.print(table)
    raise typer.Exit(1)

@app.command()
def push(
    from_: str = typer.Option(..., "--from", help="Source provider (e.g. gitlab:my-project)"),
    to: str = typer.Option(..., "--to", help="Target provider (e.g. terraform:my-workspace)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be pushed without applying"),
) -> None:
    """Push variables from source to target provider."""
    source_provider = resolve_provider(from_)
    target_provider = resolve_provider(to)

    result = diff(source_provider, target_provider)

    if result.is_clean:
        console.print("[green]✓ Everything is already in sync.[/green]")
        raise typer.Exit(0)

    to_push = result.source_only + [src for src, _ in result.differs]

    if dry_run:
        console.print(f"[yellow]Dry run — {len(to_push)} variables would be pushed:[/yellow]")
        for var in to_push:
            console.print(f"  {var.key}")
        raise typer.Exit(0)

    for var in to_push:
        target_provider.write(var)
        console.print(f"[green]✓ pushed {var.key}[/green]")

    console.print(f"\n[green]Done — {len(to_push)} variables pushed.[/green]")

def resolve_provider(source: str) -> BaseProvider:
    """Parse a provider string and return the appropriate provider."""
    if ":" not in source:
        raise ValueError("Invalid provider format. Expected 'kind:identifier'.")
    
    kind, identifier = source.split(":", 1)
    cfg = config.load()

    if kind == "env":
        return EnvFileProvider(identifier)

    if kind == "gitlab":
        if cfg.gitlab is None:
            raise ValueError("GitLab is not configured. Set GITLAB_URL, GITLAB_TOKEN, GITLAB_PROJECT_ID.")
        return GitLabProvider(url=cfg.gitlab.url, token=cfg.gitlab.token, project_id=identifier)

    if kind == "github":
        if cfg.github is None:
            raise ValueError("GitHub is not configured. Set GITHUB_TOKEN, GITHUB_ORGANIZATION, GITHUB_REPOSITORY.")
        return GitHubProvider(token=cfg.github.token, organization=cfg.github.organization, repository=identifier)

    if kind == "terraform":
        if cfg.terraform is None:
            raise ValueError("Terraform is not configured. Set TERRAFORM_TOKEN, TERRAFORM_ORGANIZATION, TERRAFORM_WORKSPACE.")
        return TerraformProvider(token=cfg.terraform.token, organization=cfg.terraform.organization, workspace=identifier)

    raise ValueError(f"Unsupported provider: {kind}")