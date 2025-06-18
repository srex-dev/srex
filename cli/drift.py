import json
from pathlib import Path
import typer
from rich import print
from rich.table import Table

app = typer.Typer(help="📉 Compare two SLO snapshots to detect drift.")


def load_snapshot(file_path: str) -> dict:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Snapshot file not found: {file_path}")
    return json.loads(path.read_text())


def calculate_drift(before: dict, after: dict) -> list:
    # Handle both 'slo' and 'slos' keys
    before_slos = {slo["name"]: slo for slo in before.get("slo", []) or before.get("slos", [])}
    after_slos = {slo["name"]: slo for slo in after.get("slo", []) or after.get("slos", [])}
    drift_report = []

    for name in after_slos:
        if name in before_slos:
            old = before_slos[name]
            new = after_slos[name]

            actual_drift = (
                new["actual"] - old["actual"]
                if isinstance(new.get("actual"), (int, float)) and isinstance(old.get("actual"), (int, float))
                else None
            )

            # Calculate error budget % drift
            budget_drift = None
            if "error_budget" in new and "consumed_budget" in new and "consumed_budget" in old:
                try:
                    delta_consumed = new["consumed_budget"] - old["consumed_budget"]
                    budget_drift = (delta_consumed / new["error_budget"]) * 100
                except (ZeroDivisionError, TypeError):
                    budget_drift = None

            drift_report.append({
                "name": name,
                "target": new.get("target"),
                "before": old.get("actual"),
                "after": new.get("actual"),
                "drift": actual_drift,
                "budget_drift_percent": round(budget_drift, 2) if budget_drift is not None else "n/a"
            })

    return drift_report


def print_drift_table(drift_data: list):
    table = Table(title="📊 SLO Drift Report", show_lines=True)
    table.add_column("SLO Name", style="bold")
    table.add_column("Target")
    table.add_column("Before", justify="right")
    table.add_column("After", justify="right")
    table.add_column("Drift", justify="right", style="yellow")
    table.add_column("Budget Drift %", justify="right", style="cyan")

    for item in drift_data:
        table.add_row(
            item["name"],
            str(item.get("target", "-")),
            str(item.get("before", "-")),
            str(item.get("after", "-")),
            f"{item['drift']:+.4f}" if isinstance(item["drift"], float) else "n/a",
            f"{item['budget_drift_percent']}%" if isinstance(item["budget_drift_percent"], (int, float)) else "n/a"
        )

    print(table)


def write_drift_output(drift_data: list, output_path: str = "output/drift_result.json"):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(json.dumps(drift_data, indent=2))
    print(f"[green]✅ Drift results written to [bold]{output_path}[/][/]")


@app.command()
def compare(
    before: str = typer.Argument(..., help="Path to the previous snapshot"),
    after: str = typer.Argument(..., help="Path to the current snapshot")
):
    """
    Compare two SLO snapshots to detect error budget drift.
    """
    try:
        before_data = load_snapshot(before)
        after_data = load_snapshot(after)
        drift_data = calculate_drift(before_data, after_data)
        if not drift_data:
            print("[bold red]⚠️ No matching SLOs found between snapshots.[/]")
        else:
            print_drift_table(drift_data)
            write_drift_output(drift_data)
    except Exception as e:
        print(f"[bold red]❌ Error:[/] {e}")


if __name__ == "__main__":
    app()