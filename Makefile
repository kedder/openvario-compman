all: test

ctags:
	ctags -R `pipenv --venv` src
	ln -sf tags .tags

test:
	pytest tests

coverage:
	pytest --cov=compman --cov-report=html --cov-report=term tests

.PHONY: black-check
black-check:
	black --check setup.py src tests

.PHONY: black
black:
	black setup.py src tests
