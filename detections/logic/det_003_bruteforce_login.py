"""
Bruteforce login attempts (stub). Enable and implement logic when ready.
"""
from typing import List

from sqlalchemy.engine import Engine

from detect.rule_loader import RuleSpec


def run(engine: Engine, rule: RuleSpec) -> List:
    # TODO: implement detection over auth_logs (e.g. many failed logins by ip/user)
    return []
