from pathlib import Path
from typing import List
import json
from .models import Alert

def write_alerts(alerts: List[Alert], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for alert in alerts:
            f.write(alert.json())
            f.write("\n")