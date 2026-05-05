"""CLI entry point for piped."""

import typer
from rich.console import Console
from rich.table import Table

from piped.differ import diff
from piped.providers.env_file import EnvFileProvider

app = typer.Typer(help="Sync CI/CD variables between platforms.")
console = Console()


@app.command()
def diff_cmd(
    source: str = typer.Option(..., "--source", "-s", help="Path to source .env file"),
    target: str = typer.Option(..., "--target", "-t", help="Path to target .env file"),
) -> None:
    """Show differences between two .env files."""
    source_provider = EnvFileProvider(source)
    target_provider = EnvFileProvider(target)

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