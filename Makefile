SHELL = /bin/sh

default:

.PHONY: deps/install
deps/install:
	pipenv install --dev --pre

.PHONY: deps/update
deps/update:
	pipenv update --dev --pre

.PHONY: black/check
black/check:
	pipenv run black --check .

.PHONY: test
test:
	pipenv run pytest --verbose --cov

.PHONY: codecov
codecov:
	pipenv run codecov

.PHONY: upload
upload: dist
	twine upload $</*

dist: setup.py
	pipenv run python $< bdist_wheel
