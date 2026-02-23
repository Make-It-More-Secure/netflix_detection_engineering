from pathlib import Path

import ui.app as ui_app


def test_list_rules_uses_project_root_rules_dir(monkeypatch):
    captured = {}

    def fake_load_rules(path: Path):
        captured["path"] = path
        return []

    monkeypatch.setattr(ui_app, "load_rules", fake_load_rules)
    monkeypatch.setattr(ui_app.templates, "TemplateResponse", lambda _name, context: context)

    response = ui_app.list_rules(request=object())

    assert captured["path"] == ui_app.PROJECT_ROOT / "detections" / "rules"
    assert response["rules"] == []
