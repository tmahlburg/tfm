init: Pipfile.lock
	pipenv install

form.py: tfm/form.ui
	pyside2-uic tfm/form.ui -o tfm/form.py

lint: tfm/*.py
	flake8 tfm/bookmarks.py --count --show-source --statistics
	flake8 main.py --count --show-source	--statistics
	flake8 tfm/stack.py --count --show-source --statistics
	flake8 tfm/tfm.py --count --show-source --statistics
	flake8 tfm/utility.py --count --show-source --statistics

docs: tfm/*.py
	cd docs/build \
	&& make html

test: tfm/*.py tests/*.py
	pytest

.PHONY:	init form.py lint help Makefile
