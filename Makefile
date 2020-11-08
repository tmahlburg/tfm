init: Pipfile.lock
	pipenv install

form.py: form.ui
	pipenv run pyside2-uic form.ui -o form.py

lint: tfm/bookmarks.py tfm/main.py tfm/stack.py	tfm/tfm.py tfm/utility.py
		pipenv run flake8 tfm/bookmarks.py --count --show-source --statistics
		pipenv run flake8 tfm/main.py --count --show-source	--statistics
		pipenv run flake8 tfm/stack.py --count --show-source --statistics
		pipenv run flake8 tfm/tfm.py --count --show-source --statistics
		pipenv run flake8 tfm/utility.py --count --show-source --statistics

.PHONY:	init form.py lint
