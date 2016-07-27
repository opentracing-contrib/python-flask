.PHONY: test publish install clean clean-build clean-pyc clean-test build upload-docs

install: 
	python setup.py install

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

test: 
	python setup.py test
	make -C docs doctest

build: 
	python setup.py build

upload-docs:
	python setup.py build_sphinx
	python setup.py upload_docs

# The publish step does a clean and rebuild as the `gradle build` hasn't seemed
# 100% reliable in rebuilding when files are changed (?).  This may very much be
# a setup error -- but for now, a clean build is done just in case.
#
# See https://bintray.com/lightstep for published artifacts
publish: clean test build
	@git diff-index --quiet HEAD || (echo "git has uncommitted changes. Refusing to publish." && false)
	awk 'BEGIN { FS = "." }; { printf("%d.%d.%d", $$1, $$2, $$3+1) }' VERSION > VERSION.incr
	mv VERSION.incr VERSION
	git add VERSION
	git commit -m "Update VERSION"
	git tag `cat VERSION`
	git push
	git push --tags
	python setup.py register -r pypitest || (echo "Was unable to register to pypitest, aborting publish." && false)
	python setup.py sdist upload -r pypitest || (echo "Was unable to upload to pypitest, ablorint publish." && false)
	python setup.py register -r pypi || (echo "Was unable to register to pypi, aborting publish." && false)
	python setup.py sdist upload -r pypi || (echo "Was unable to upload to pypi, publish failed." && false)
	upload-docs
	@echo
	@echo "\033[92mSUCCESS: published v`cat VERSION` \033[0m"
	@echo
