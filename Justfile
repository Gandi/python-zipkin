package := 'zipkin'
default_test_suite := 'zipkin/tests'

install:
    poetry install --with dev

doc:
    cd docs && poetry run make html
    xdg-open docs/build/html/index.html

cleandoc:
    cd docs && poetry run make clean

test: unittest

lf:
    poetry run pytest -sxvvv --lf

unittest test_suite=default_test_suite:
    poetry run pytest -sxv {{test_suite}}

lint:
    poetry run flake8

mypy:
    poetry run mypy src/

black:
    poetry run isort .
    poetry run black .

fmt: black

gh-pages:
    poetry export --with doc -f requirements.txt -o docs/requirements.txt --without-hashes

cov test_suite=default_test_suite:
    rm -f .coverage
    rm -rf htmlcov
    poetry run pytest --cov-report=html --cov={{package}} {{test_suite}}
    xdg-open htmlcov/index.html

release major_minor_patch: test && changelog
    poetry version {{major_minor_patch}}
    poetry install

changelog:
    poetry run python scripts/write_changelog.py
    cat CHANGES.rst >> CHANGES.rst.new
    rm CHANGES.rst
    mv CHANGES.rst.new CHANGES.rst
    $EDITOR CHANGES.rst

publish:
    git commit -am "Release $(poetry version -s --no-ansi)"
    poetry build
    poetry publish
    git push
    git tag "$(poetry version -s --no-ansi)"
    git push origin "$(poetry version -s --no-ansi)"
