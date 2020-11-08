UI_TO_PY_CONVERTER

init: Pipfile
    pipenv install

form.py: form.ui
    pipenv run pyside2-uic form.ui -o form.py
