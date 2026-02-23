import click
from pathlib import Path
from .runner import run_all
from .db import get_engine, init_schema

@click.group()
def cli():
    pass

@cli.command()
def initdb():
    """Create tables."""
    engine = get_engine()
    init_schema(engine)
    click.echo("DB schema initialized.")

@cli.command()
@click.option("--rule-dir", default="detections/rules", type=click.Path())
@click.option("--out", default="alerts/alerts.jsonl", type=click.Path())
def run(rule_dir, out):
    """Run all enabled rules."""
    run_all(Path(rule_dir), Path(out))
    click.echo(f"Alerts written to {out}")


if __name__ == "__main__":
    cli()