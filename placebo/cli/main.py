"""
Placebo CLI Tool.
Command-line interface for local audits, ledger inspection, and initialization.
"""

from datetime import datetime
import json
import os
import typer
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from placebo import __version__
from placebo.models.hypothesis import Hypothesis, MetricDefinition, TimeWindow
from placebo.models.verdict import VerdictGrade
from placebo.pipeline.runner import AuditPipeline
from placebo.storage.sqlite import SQLiteStorage

app = typer.Typer(help="Placebo: Falsification & Statistical Audit Layer for AI Data Agents")
console = Console()


@app.command()
def version():
    """Print the Placebo version."""
    console.print(f"[bold cyan]Placebo[/bold cyan] version [green]{__version__}[/green]")


@app.command()
def init(db_path: str = "./placebo_ledger.db"):
    """Initialize the local Placebo SQLite ledger and check environment."""
    storage = SQLiteStorage(db_path=db_path)
    console.print(f"[bold green]✓[/bold green] Initialized Placebo SQLite ledger at: [bold]{db_path}[/bold]")


@app.command()
def ledger(session_id: str = typer.Option(None, help="Filter by session ID"), db_path: str = "./placebo_ledger.db"):
    """List registered hypotheses and audits in the ledger."""
    storage = SQLiteStorage(db_path=db_path)
    hyps = storage.list_hypotheses(session_id=session_id)

    if not hyps:
        console.print("[yellow]No hypotheses registered yet.[/yellow]")
        return

    table = Table(title="Placebo Hypothesis Ledger")
    table.add_column("Hypothesis ID", style="cyan", no_wrap=True)
    table.add_column("Session ID", style="magenta")
    table.add_column("Metric", style="green")
    table.add_column("Intervention Date", style="yellow")
    table.add_column("Claim Description")

    for h in hyps:
        table.add_row(
            h.hypothesis_id,
            h.session_id,
            h.metric.name,
            h.time_window.intervention_date or "N/A",
            h.claim_description
        )

    console.print(table)


@app.command()
def audit(
    data_file: str = typer.Argument(..., help="Path to CSV dataset"),
    metric_col: str = typer.Option(..., "--metric", "-m", help="Metric column name"),
    date_col: str = typer.Option(..., "--date-col", "-d", help="Date column name"),
    intervention_date: str = typer.Option(..., "--intervention", "-i", help="Intervention date (YYYY-MM-DD)"),
    entity_col: str = typer.Option("entity_id", "--entity", "-e", help="Entity or user ID column"),
    claim: str = typer.Option("Automated data audit", "--claim", "-c", help="Claim description"),
    output_json: str = typer.Option(None, "--output", "-o", help="Optional output JSON path"),
    db_path: str = "./placebo_ledger.db"
):
    """Run an active falsification audit on a dataset."""
    if not os.path.exists(data_file):
        console.print(f"[bold red]Error:[/bold red] File not found: {data_file}")
        raise typer.Exit(code=1)

    console.print(f"[bold cyan]Reading dataset:[/bold cyan] {data_file}")
    df = pd.read_csv(data_file)

    storage = SQLiteStorage(db_path=db_path)
    pipeline = AuditPipeline(storage=storage)

    hyp = Hypothesis(
        hypothesis_id=f"HYP-CLI-{datetime.utcnow().strftime('%H%M%S')}",
        session_id="cli_session",
        claim_description=claim,
        metric=MetricDefinition(name=metric_col, column=metric_col, aggregation="mean"),
        time_window=TimeWindow(
            start=str(df[date_col].min()),
            end=str(df[date_col].max()),
            intervention_date=intervention_date
        )
    )

    console.print("[bold yellow]Executing statistical tests and falsification battery...[/bold yellow]")
    package = pipeline.run_audit(
        hypothesis=hyp,
        df=df,
        entity_col=entity_col,
        date_col=date_col,
        metric_col=metric_col
    )

    # Render results
    grade_color = "green" if package.verdict.grade == VerdictGrade.CONFIRMED else "red"
    console.print(Panel(
        f"[bold {grade_color}]VERDICT: {package.verdict.grade.value}[/bold {grade_color}]\n"
        f"Confidence: {package.verdict.confidence.value}\n\n"
        f"{package.verdict.summary}\n\n"
        f"[bold]Effect Size:[/bold] {package.statistical_result.effect_size} "
        f"(Raw p: {package.statistical_result.raw_p_value}, Adj p: {package.statistical_result.adjusted_p_value})\n"
        f"[bold]Recommendation:[/bold] {package.verdict.recommendation}",
        title=f"Audit Package: {package.audit_id}",
        border_style=grade_color
    ))

    # Falsification tests summary
    table = Table(title="Falsification Test Results")
    table.add_column("Test Type", style="cyan")
    table.add_column("Status")
    table.add_column("Details")

    for f in package.falsification_results:
        status_style = "green" if f.status.value == "PASSED" else "red" if f.status.value == "FAILED" else "yellow"
        table.add_row(f.test_type.value, f"[{status_style}]{f.status.value}[/{status_style}]", f.details)

    console.print(table)

    if output_json:
        with open(output_json, "w") as out:
            out.write(package.model_dump_json(indent=2))
        console.print(f"[green]Saved Evidence Package to:[/green] {output_json}")


if __name__ == "__main__":
    app()
