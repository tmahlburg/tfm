init: Pipfile
    pipenv install

form.py: form.ui
    pipenv run pyside2-uic form.ui -o form.py

lint:
    pipenv run flake8 tfm --count --show-source --statistics
