project := flask_opentracing

pytest := PYTHONDONTWRITEBYTECODE=1 py.test --tb short -rxs \
	--cov-report term-missing:skip-covered --cov=$(project) tests

.PHONY: test publish install clean clean-build clean-pyc clean-test build upload-docs

install: 
	python setup.py install

check-virtual-env:
	@echo virtual-env: $${VIRTUAL_ENV?"Please run in virtual-env"}

bootstrap: check-virtual-env
	pip install -r requirements.txt
	pip install -r requirements-test.txt
	python setup.py develop

clean: clean-build clean-pyc clean-test

clean-build:
	python setup.py clean
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	rm -fr .cache/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -rf {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -f .coverage
	rm -f coverage.xml
	rm -fr htmlcov/

lint:
	flake8 $(project) tests

test:
	$(pytest)

build: 
	python setup.py build

docs:
	make -C docs doctest

upload-docs:
	git submodule update --init  # for sphinx flask theme
	python setup.py build_sphinx
	python setup.py upload_docs

publish: clean test build
	@git diff-index --quiet HEAD || (echo "git has uncommitted changes. Refusing to publish." && false)
	awk 'BEGIN { FS = "." }; { printf("%d.%d.%d", $$1, $$2, $$3+1) }' VERSION > VERSION.incr
	mv VERSION.incr VERSION
	git add VERSION
	git commit -m "Update VERSION"
	git tag `cat VERSION`
	git push
	git push --tags
	python setup.py register -r pypi || (echo "Was unable to register to pypi, aborting publish." && false)
	python setup.py sdist upload -r pypi || (echo "Was unable to upload to pypi, publish failed." && false)
	$(MAKE) upload-docs
	@echo
	@echo "\033[92mSUCCESS: published v`cat VERSION` \033[0m"
	@echo
