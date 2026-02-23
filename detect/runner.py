import logging
from importlib import import_module
from pathlib import Path
from typing import List
from sqlalchemy.engine import Engine
from .rule_loader import RuleSpec, load_rules
from .alerts import write_alerts
from .db import get_engine

logger = logging.getLogger(__name__)

def run_all(rule_dir: Path, alerts_out: Path) -> None:
    """Load all enabled rules and execute them."""
    try:
        engine = get_engine()
        logger.info(f"Loading rules from {rule_dir}")
        rules = load_rules(rule_dir)
        enabled_rules = [r for r in rules if r.enabled]
        logger.info(f"Found {len(rules)} rules, {len(enabled_rules)} enabled")
        
        all_alerts = []
        for rule in enabled_rules:
            try:
                logger.info(f"Running rule {rule.id}: {rule.name}")
                alerts = run_rule(rule, engine)
                logger.info(f"Rule {rule.id} generated {len(alerts)} alerts")
                all_alerts.extend(alerts)
            except Exception as e:
                logger.error(f"Error running rule {rule.id}: {e}", exc_info=True)
                continue  # Continue with other rules on error
        
        logger.info(f"Total alerts generated: {len(all_alerts)}")
        write_alerts(all_alerts, alerts_out)
        logger.info(f"Alerts written to {alerts_out}")
        
    except Exception as e:
        logger.error(f"Failed to run detection pipeline: {e}", exc_info=True)
        raise


def run_rule(rule: RuleSpec, engine: Engine) -> List:
    """Execute a single rule and return generated alerts."""
    try:
        module = import_module(f"detections.logic.{rule.logic_module}")
        # convention: each logic module exposes `run(engine, rule: RuleSpec) -> List[Alert]`
        if not hasattr(module, 'run'):
            raise AttributeError(f"Module {rule.logic_module} does not have 'run' function")
        
        return module.run(engine, rule)
        
    except ImportError as e:
        logger.error(f"Failed to import detection module {rule.logic_module}: {e}")
        raise
    except Exception as e:
        logger.error(f"Detection logic error in {rule.logic_module}: {e}", exc_info=True)
        raise