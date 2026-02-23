.PHONY: up initdb seed run test

PYTHON = .venv/bin/python

up:
	docker compose up -d

initdb:
	$(PYTHON) -m detect.cli initdb

seed:
	$(PYTHON) -m detect.load_sample_data

run:
	$(PYTHON) -m detect.cli run

test:
	$(PYTHON) -m pytest -q

ui:
	$(PYTHON) -m uvicorn ui.app:app --reload
