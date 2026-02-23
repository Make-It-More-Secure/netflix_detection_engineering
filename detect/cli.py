import logging
import click
from pathlib import Path
from .runner import run_all
from .db import get_engine, init_schema
from .config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@click.group()
def cli():
    """Detection engineering CLI."""
    pass

@cli.command()
def initdb():
    """Initialize database schema (drops existing tables)."""
    try:
        engine = get_engine()
        init_schema(engine)
        click.echo("✓ DB schema initialized successfully.")
    except Exception as e:
        click.echo(f"✗ Failed to initialize schema: {e}", err=True)
        raise SystemExit(1)

@cli.command()
@click.option("--rule-dir", default="detections/rules", type=click.Path(exists=True))
@click.option("--out", default="alerts/alerts.jsonl", type=click.Path())
def run(rule_dir, out):
    """Run all enabled detection rules."""
    try:
        click.echo(f"Starting detection pipeline...")
        run_all(Path(rule_dir), Path(out))
        click.echo(f"✓ Detection complete. Alerts written to {out}")
    except Exception as e:
        click.echo(f"✗ Detection pipeline failed: {e}", err=True)
        raise SystemExit(1)


if __name__ == "__main__":
    cli()