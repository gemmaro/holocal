# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile intl docs intl-dev run

run:
	poetry run python run.py

docs:
	${MAKE} html
	rsync -av build/html/ public/
	${MAKE} intl
	rsync -av build/html/ public/en/

intl:
	[ "${CI}" = yes ] || ${MAKE} intl-dev
	${MAKE} -e SPHINXOPTS="-D language='en'" html

intl-dev:
	${MAKE} gettext
	sphinx-intl update -p build/gettext

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
