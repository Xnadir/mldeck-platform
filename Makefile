.PHONY: run test lint clean docker

run:
	python app.py

test:
	python -m pytest tests/ -v --tb=short

lint:
	flake8 *.py --max-line-length 120
	isort --check-only *.py

clean:
	rm -rf __pycache__ .pytest_cache experiments_log.json model_registry.json

docker:
	docker build -t mldeck .
	docker run -p 8000:8000 mldeck
