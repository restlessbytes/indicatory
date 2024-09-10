default:
    @just --list

install:
    @poetry install

lint:
    @poetry run ruff check indicatory/

lintf:
    @poetry run ruff check --fix indicatory/

fmt:
    @poetry run ruff format *.py
    @poetry run ruff format indicatory/
    @poetry run ruff format tests/

check:
    @poetry run pyright indicatory/

test test_file:
    @poetry run pytest -vv {{test_file}}

test_all:
    @poetry run pytest -vv tests/
