import json
from pathlib import Path
import typer
from rich import print
from rich.table import Table
from rich.panel import Panel

app = typer.Typer(help="📋 Generate a scorecard from an SLO snapshot.")


def load_snapshot(file_path: str) -> dict:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Snapshot file not found: {file_path}")
    return json.loads(path.read_text())


def calculate_scorecard(snapshot: dict) -> dict:
    # Handle both 'slo' and 'slos' keys
    slos = snapshot.get("slo", []) or snapshot.get("slos", [])
    total = len(slos)
    passing = 0

    for slo in slos:
        try:
            if slo.get("actual") is not None and slo.get("target") is not None:
                if float(slo["actual"]) >= float(slo["target"]):
                    passing += 1
        except (ValueError, TypeError):
            continue

    score = round((passing / total) * 100, 2) if total > 0 else 0.0

    return {
        "total_slos": total,
        "passing_slos": passing,
        "failing_slos": total - passing,
        "slo_pass_rate": score,
        "slos": slos
    }


def print_scorecard_table(scorecard: dict):
    print(Panel.fit(
        f"[bold cyan]📊 SRE Scorecard[/] — "
        f"[green]{scorecard['passing_slos']} passing[/] / "
        f"[red]{scorecard['failing_slos']} failing[/] "
        f"({scorecard['slo_pass_rate']}% pass rate)"
    ))

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("SLO Name", style="bold")
    table.add_column("Target", justify="right")
    table.add_column("Actual", justify="right")
    table.add_column("Result", justify="center")

    for slo in scorecard["slos"]:
        name = slo.get("name", "Unnamed")
        target = slo.get("target", "-")
        actual = slo.get("actual", "-")
        try:
            passed = float(actual) >= float(target)
        except (ValueError, TypeError):
            passed = False
        result = "✅ Pass" if passed else "❌ Fail"
        table.add_row(name, str(target), str(actual), result)

    print(table)


def save_scorecard(scorecard: dict, format: str, output_path: str):
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if format == "json":
        path.write_text(json.dumps(scorecard, indent=2))
    elif format == "markdown":
        lines = ["# 📋 SRE Scorecard", f"- Pass Rate: **{scorecard['slo_pass_rate']}%**", ""]
        lines.append("| SLO | Target | Actual | Result |")
        lines.append("|-----|--------|--------|--------|")
        for slo in scorecard["slos"]:
            name = slo.get("name", "Unnamed")
            target = slo.get("target", "-")
            actual = slo.get("actual", "-")
            try:
                passed = float(actual) >= float(target)
            except (ValueError, TypeError):
                passed = False
            result = "✅ Pass" if passed else "❌ Fail"
            lines.append(f"| {name} | {target} | {actual} | {result} |")
        path.write_text("\n".join(lines))


@app.command()
def generate(
    snapshot: str = typer.Option(..., "--snapshot", "-s", help="Path to the SLO snapshot JSON file"),
    format: str = typer.Option(None, "--format", "-f", help="Output format (json or markdown)"),
    output: str = typer.Option(None, "--output", "-o", help="Output file path")
):
    """
    Generate a scorecard report from an SLO snapshot.
    """
    try:
        snapshot_data = load_snapshot(snapshot)
        scorecard = calculate_scorecard(snapshot_data)
        print_scorecard_table(scorecard)

        if format and output:
            format = format.lower()
            if format not in ("json", "markdown"):
                raise ValueError("Format must be 'json' or 'markdown'")
            save_scorecard(scorecard, format, output)
            print(f"[green]✅ Scorecard saved to [bold]{output}[/] as {format}.")

    except Exception as e:
        print(f"[bold red]❌ Error:[/] {e}")


if __name__ == "__main__":
    app()