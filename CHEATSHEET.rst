Tips
====

To run tests
------------

* Install requirements: ``pip install -e ".[test]"``
  (possibly in a virtualenv)

* Actually run the tests: ``pytest sniffio``


To run yapf
-----------

* Show what changes yapf wants to make: ``yapf -rpd sniffio``

* Apply all changes directly to the source tree: ``yapf -rpi sniffio``


To make a release
-----------------

* Update the version in ``sniffio/_version.py``

* Run ``towncrier`` to collect your release notes.

* Review your release notes.

* Check everything in.

* Double-check it all works, docs build, etc.

* Build your sdist and wheel: ``python -m build``

* Upload to PyPI: ``twine upload dist/*``

* Use ``git tag`` to tag your version.

* Don't forget to ``git push --tags``.