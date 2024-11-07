# make clean targets

# generate Sphinx HTML documentation, including API docs
#

.PHONY: install-docs docs clean-docs servedocs 

### install documentation build dependencies
install-docs:
	pip install -f dist -U .[docs]

### rebuild documentation
docs: install-docs clean-docs docs/readme.rst
	sphinx-apidoc -o docs/ $(module)
	$(MAKE) -C docs html
	$(browser) docs/_build/html/index.html

# clean up documentation files
docs-clean:
	rm -f docs/$(project).rst
	rm -f docs/modules.rst

docs-sterile:
	@:

### run a dev-mode docs webserver; recompiling on changes 
servedocs: docs
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

docs/readme.rst: README.md
	m2r2 --overwrite $<
	mv README.rst $@

