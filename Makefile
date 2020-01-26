ctags:
	ctags -R `pipenv --venv` src
	ln -sf tags .tags
