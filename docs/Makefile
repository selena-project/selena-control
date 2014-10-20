# Makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
PAPER         =
BUILDDIR      = ./output

# User-friendly check for sphinx-build
ifeq ($(shell which $(SPHINXBUILD) >/dev/null 2>&1; echo $$?), 1)
$(error The '$(SPHINXBUILD)' command was not found. Make sure you have Sphinx installed, then set the SPHINXBUILD environment variable to point to the full path of the '$(SPHINXBUILD)' executable. Alternatively you can add the directory with the executable to your PATH. If you don't have Sphinx installed, grab it from http://sphinx-doc.org/)
endif

# Internal variables.
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
ALLSPHINXOPTS_API   = -d $(BUILDDIR)/api/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) src/api
ALLSPHINXOPTS_MANUAL   = -d $(BUILDDIR)/manual/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) src/manual
# the i18n builder cannot share the environment and doctrees with the others
I18NSPHINXOPTS  = $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) src

.PHONY: help clean html dirhtml singlehtml pickle json htmlhelp qthelp devhelp epub latex latexpdf text man changes linkcheck doctest gettext

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  html       to make standalone HTML files"
	@echo "  dirhtml    to make HTML files named index.html in directories"
	@echo "  singlehtml to make a single large HTML file"
	@echo "  pickle     to make pickle files"
	@echo "  json       to make JSON files"
	@echo "  htmlhelp   to make HTML files and a HTML help project"
	@echo "  qthelp     to make HTML files and a qthelp project"
	@echo "  devhelp    to make HTML files and a Devhelp project"
	@echo "  epub       to make an epub"
	@echo "  latex      to make LaTeX files, you can set PAPER=a4 or PAPER=letter"
	@echo "  latexpdf   to make LaTeX files and run them through pdflatex"
	@echo "  latexpdfja to make LaTeX files and run them through platex/dvipdfmx"
	@echo "  text       to make text files"
	@echo "  man        to make manual pages"
	@echo "  texinfo    to make Texinfo files"
	@echo "  info       to make Texinfo files and run them through makeinfo"
	@echo "  gettext    to make PO message catalogs"
	@echo "  changes    to make an overview of all changed/added/deprecated items"
	@echo "  xml        to make Docutils-native XML files"
	@echo "  pseudoxml  to make pseudoxml-XML files for display purposes"
	@echo "  linkcheck  to check all external links for integrity"
	@echo "  doctest    to run all doctests embedded in the documentation (if enabled)"

clean:
	rm -rf $(BUILDDIR)/*

html:
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS_API) $(BUILDDIR)/api/html
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS_MANUAL) $(BUILDDIR)/manual/html
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

dirhtml:
	$(SPHINXBUILD) -b dirhtml $(ALLSPHINXOPTS_API) $(BUILDDIR)/api/dirhtml
	$(SPHINXBUILD) -b dirhtml $(ALLSPHINXOPTS_MANUAL) $(BUILDDIR)/manual/dirhtml
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/dirhtml."

singlehtml:
	$(SPHINXBUILD) -b singlehtml $(ALLSPHINXOPTS_API) $(BUILDDIR)/api/singlehtml
	$(SPHINXBUILD) -b singlehtml $(ALLSPHINXOPTS_MANUAL) $(BUILDDIR)/manual/singlehtml
	@echo
	@echo "Build finished. The HTML page is in $(BUILDDIR)/singlehtml."

pickle:
	$(SPHINXBUILD) -b pickle $(ALLSPHINXOPTS_API) $(BUILDDIR)/api/pickle
	$(SPHINXBUILD) -b pickle $(ALLSPHINXOPTS_MANUAL) $(BUILDDIR)/manual/pickle
	@echo
	@echo "Build finished; now you can process the pickle files."

json:
	$(SPHINXBUILD) -b json $(ALLSPHINXOPTS_API) $(BUILDDIR)/api/json
	$(SPHINXBUILD) -b json $(ALLSPHINXOPTS_MANUAL) $(BUILDDIR)/manual/json
	@echo
	@echo "Build finished; now you can process the JSON files."

htmlhelp:
	$(SPHINXBUILD) -b htmlhelp $(ALLSPHINXOPTS_API) $(BUILDDIR)/api/htmlhelp
	$(SPHINXBUILD) -b htmlhelp $(ALLSPHINXOPTS_MANUAL) $(BUILDDIR)/manual/htmlhelp
	@echo
	@echo "Build finished; now you can run HTML Help Workshop with the" \
	      ".hhp project file in $(BUILDDIR)/htmlhelp."

qthelp:
	$(SPHINXBUILD) -b qthelp $(ALLSPHINXOPTS_API) $(BUILDDIR)/api/qthelp
	$(SPHINXBUILD) -b qthelp $(ALLSPHINXOPTS_MANUAL) $(BUILDDIR)/manual/qthelp
	@echo
	@echo "Build finished; now you can run "qcollectiongenerator" with the" \
	      ".qhcp project file in $(BUILDDIR)/qthelp, like this:"
	@echo "# qcollectiongenerator $(BUILDDIR)/qthelp/Selena.qhcp"
	@echo "To view the help file:"
	@echo "# assistant -collectionFile $(BUILDDIR)/qthelp/Selena.qhc"

devhelp:
	$(SPHINXBUILD) -b devhelp $(ALLSPHINXOPTS_API) $(BUILDDIR)/api/devhelp
	$(SPHINXBUILD) -b devhelp $(ALLSPHINXOPTS_MANUAL) $(BUILDDIR)/manual/devhelp
	@echo
	@echo "Build finished."
	@echo "To view the help file:"
	@echo "# mkdir -p $$HOME/.local/share/devhelp/Selena"
	@echo "# ln -s $(BUILDDIR)/devhelp $$HOME/.local/share/devhelp/Selena"
	@echo "# devhelp"

epub:
	$(SPHINXBUILD) -b epub $(ALLSPHINXOPTS_API) $(BUILDDIR)/api/epub
	$(SPHINXBUILD) -b epub $(ALLSPHINXOPTS_MANUAL) $(BUILDDIR)/manual/epub
	@echo
	@echo "Build finished. The epub file is in $(BUILDDIR)/epub."

latex:
	$(SPHINXBUILD) -b latex $(ALLSPHINXOPTS_API) $(BUILDDIR)/api/latex
	$(SPHINXBUILD) -b latex $(ALLSPHINXOPTS_MANUAL) $(BUILDDIR)/manual/latex
	@echo
	@echo "Build finished; the LaTeX files are in $(BUILDDIR)/latex."
	@echo "Run \`make' in that directory to run these through (pdf)latex" \
	      "(use \`make latexpdf' here to do that automatically)."

latexpdf:
	$(SPHINXBUILD) -b latex $(ALLSPHINXOPTS_API) $(BUILDDIR)/api/latex
	$(SPHINXBUILD) -b latex $(ALLSPHINXOPTS_MANUAL) $(BUILDDIR)/manual/latex
	@echo "Running LaTeX files through pdflatex..."
	$(MAKE) -C $(BUILDDIR)/api/latex all-pdf
	$(MAKE) -C $(BUILDDIR)/manual/latex all-pdf
	@echo "pdflatex finished; the PDF files are in $(BUILDDIR)/latex."

latexpdfja:
	$(SPHINXBUILD) -b latex $(ALLSPHINXOPTS_API) $(BUILDDIR)/api/latex
	$(SPHINXBUILD) -b latex $(ALLSPHINXOPTS_MANUAL) $(BUILDDIR)/manual/latex
	@echo "Running LaTeX files through platex and dvipdfmx..."
	$(MAKE) -C $(BUILDDIR)/api/latex all-pdf-ja
	$(MAKE) -C $(BUILDDIR)/manual/latex all-pdf-ja
	@echo "pdflatex finished; the PDF files are in $(BUILDDIR)/latex."

text:
	$(SPHINXBUILD) -b text $(ALLSPHINXOPTS_API) $(BUILDDIR)/api/text
	$(SPHINXBUILD) -b text $(ALLSPHINXOPTS_MANUAL) $(BUILDDIR)/manual/text
	@echo
	@echo "Build finished. The text files are in $(BUILDDIR)/text."

man:
	$(SPHINXBUILD) -b man $(ALLSPHINXOPTS_API) $(BUILDDIR)/api/man
	$(SPHINXBUILD) -b man $(ALLSPHINXOPTS_MANUAL) $(BUILDDIR)/manual/man
	@echo
	@echo "Build finished. The manual pages are in $(BUILDDIR)/man."

texinfo:
	$(SPHINXBUILD) -b texinfo $(ALLSPHINXOPTS_API) $(BUILDDIR)/api/texinfo
	$(SPHINXBUILD) -b texinfo $(ALLSPHINXOPTS_MANUAL) $(BUILDDIR)/manual/texinfo
	@echo
	@echo "Build finished. The Texinfo files are in $(BUILDDIR)/texinfo."
	@echo "Run \`make' in that directory to run these through makeinfo" \
	      "(use \`make info' here to do that automatically)."

info:
	$(SPHINXBUILD) -b texinfo $(ALLSPHINXOPTS_API) $(BUILDDIR)/api/texinfo
	$(SPHINXBUILD) -b texinfo $(ALLSPHINXOPTS_MANUAL) $(BUILDDIR)/manual/texinfo
	@echo "Running Texinfo files through makeinfo..."
	make -C $(BUILDDIR)/api/texinfo info
	make -C $(BUILDDIR)/manual/texinfo info
	@echo "makeinfo finished; the Info files are in $(BUILDDIR)/texinfo."

gettext:
	$(SPHINXBUILD) -b gettext $(ALLSPHINXOPTS_API) $(BUILDDIR)/api/gettext
	$(SPHINXBUILD) -b gettext $(ALLSPHINXOPTS_MANUAL) $(BUILDDIR)/manual/gettext
	@echo
	@echo "Build finished. The message catalogs are in $(BUILDDIR)/locale."

changes:
	$(SPHINXBUILD) -b changes $(ALLSPHINXOPTS_API) $(BUILDDIR)/api/changes
	$(SPHINXBUILD) -b changes $(ALLSPHINXOPTS_MANUAL) $(BUILDDIR)/manual/changes
	@echo
	@echo "The overview file is in $(BUILDDIR)/changes."

linkcheck:
	$(SPHINXBUILD) -b linkcheck $(ALLSPHINXOPTS_API) $(BUILDDIR)/api/linkcheck
	$(SPHINXBUILD) -b linkcheck $(ALLSPHINXOPTS_MANUAL) $(BUILDDIR)/manual/linkcheck
	@echo
	@echo "Link check complete; look for any errors in the above output " \
	      "or in $(BUILDDIR)/linkcheck/output.txt."

doctest:
	$(SPHINXBUILD) -b doctest $(ALLSPHINXOPTS_API) $(BUILDDIR)/api/doctest
	$(SPHINXBUILD) -b doctest $(ALLSPHINXOPTS_MANUAL) $(BUILDDIR)/manual/doctest
	@echo "Testing of doctests in the sources finished, look at the " \
	      "results in $(BUILDDIR)/doctest/output.txt."

xml:
	$(SPHINXBUILD) -b xml $(ALLSPHINXOPTS_API) $(BUILDDIR)/api/xml
	$(SPHINXBUILD) -b xml $(ALLSPHINXOPTS_MANUAL) $(BUILDDIR)/manual/xml
	@echo
	@echo "Build finished. The XML files are in $(BUILDDIR)/xml."

pseudoxml:
	$(SPHINXBUILD) -b pseudoxml $(ALLSPHINXOPTS_API) $(BUILDDIR)/api/pseudoxml
	$(SPHINXBUILD) -b pseudoxml $(ALLSPHINXOPTS_MANUAL) $(BUILDDIR)/manual/pseudoxml
	@echo
	@echo "Build finished. The pseudo-XML files are in $(BUILDDIR)/pseudoxml."
