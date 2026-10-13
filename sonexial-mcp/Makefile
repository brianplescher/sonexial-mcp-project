.PHONY: install seed run-stdio run-http test clean docker-build docker-up

install:
	pip install -r requirements.txt

seed:
	python -m sonexial_mcp.seed

run-stdio:
	python -m sonexial_mcp.cli --transport stdio

run-http:
	python -m sonexial_mcp.cli --transport http

test:
	pytest -v

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -f sonexial.db
	rm -rf .pytest_cache

docker-build:
	docker compose build

docker-up:
	docker compose up --build

docker-down:
	docker compose down
