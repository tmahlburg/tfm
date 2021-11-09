init: Pipfile.lock
	pipenv install

form.py: tfm/form.ui
	pyside6-uic tfm/form.ui -o tfm/form.py

lint: tfm/*.py
	flake8 tfm/bookmarks.py --count --show-source --statistics
	flake8 tfm/__main__.py --count --show-source	--statistics
	flake8 tfm/stack.py --count --show-source --statistics
	flake8 tfm/tfm.py --count --show-source --statistics
	flake8 tfm/utility.py --count --show-source --statistics
	flake8 tfm/paste_worker.py --count --show-source --statistics
	flake8 tfm/mounts_model.py --count --show-source --statistics

docs: tfm/*.py
	cd docs/ \
	&& make html

test: tfm/*.py tests/*.py
	pytest

build: tfm/*.py setup.py pyproject.toml
	python3 -m build

upload: dist/*.tar.gz dist/*.whl
	python3 -m twine upload dist/*

.PHONY:	init form.py lint help docs test build upload Makefile
