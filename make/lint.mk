# python lint makefile

lint_line_length := 120
lint_python_version := 310

ISORT_OPTS = --py $(lint_python_version) --profile black --gitignore
BLACK_OPTS = --target-version py$(lint_python_version) --line-length $(lint_line_length)
FLAKE8_OPTS = --max-line-length $(lint_line_length)

export ISORT_OPTS
export BLACK_OPTS
export FLAKE8_OPTS

.fmt: $(python_src)
	isort $(ISORT_OPTS) $(src_dirs)
	black $(BLACK_OPTS) $(src_dirs)
	flake8 $(FLAKE8_OPTS) $(src_dirs)
	touch $@

### format source and lint
fmt:	.fmt

### vim autofix
fix:
	fixlint $(src_dirs)

lint-clean:
	rm -f .black .flake8 .errors .fmt

lint-sterile:
	@:
