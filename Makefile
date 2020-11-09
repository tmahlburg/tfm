init: Pipfile.lock
	pipenv install

form.py: form.ui
	pyside2-uic form.ui -o form.py

lint:
	flake8 tfm/bookmarks.py --count --show-source --statistics
	flake8 main.py --count --show-source	--statistics
	flake8 tfm/stack.py --count --show-source --statistics
	flake8 tfm/tfm.py --count --show-source --statistics
	flake8 tfm/utility.py --count --show-source --statistics

docs: tfm/*.py
	cd docs/build \
	&& make html

.PHONY:	init form.py lint help Makefile
