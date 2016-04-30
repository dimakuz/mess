PKG=mess
PEP8=pep8


check: pep8 unittests

pep8:
	find $(PKG) -type f -name '*.py' | xargs $(PEP8)

unittests:
	PYTHONPATH=$(PYTHONPATH):$(PKG) py.test $(wildcard tests/*_tests.py)

.PHONY: pep8 unittests check
