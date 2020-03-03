ctags:
	ctags -R `pipenv --venv` src
	ln -sf tags .tags

test:
	pytest tests

coverage:
	pytest --cov=compman --cov-report=html --cov-report=term tests
