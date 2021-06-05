How to contribute to Flask Inertia ?
####################################

Thank you for considering contributing to Flask-Inertia. You can contribute in
many ways. For example:

**Did you find a bug ?**

Feel free to open a new issue on `Github <https://github.com/j0ack/flask-inertia/issues/new/choose>`_
after ensuring there are no open issue addressing the problem. Please include a
title and a clear description of the issue in the ticket.

When filling a new issue, make sure to include these information:

* What version of Python, Flask and InertiaJS are you using ?
* What operating System are you using ?
* What did you do ?
* What did you expect to see ?

**Do you want to suggest a feature ?**

If you find yourself wishing for a feature that doesn't exist please open an
issue on our issues list on GitHub which describes the feature you would like to
see, why you need it, and how it should work.

**Did you write documentation or `how-to` articles and want it referenced here ?**

Please open a new Pull Request on Github referencing your work in the `README.rst`
file. If you're not familiar on how to open a PR, please see the documentation
at http://makeapullrequest.com/.

**Did you code a new feature or a bug fix ?**

Let us know what you plan in the GitHub Issue tracker so we can provide feedback.
Provide tests and documentation whenever possible. It is very unlikely that we
will accept new features or functionality without the proper testing and
documentation. Open a GitHub Pull Request with your patches and we will review
your contribution and respond as quickly as possible.

Please refer to the Guidelines below and be sure your contribution respects it.


Guidelines
==========

Code formatting
---------------

Flask-Inertia uses the `pre-commit <https://pre-commit.com/>`_ project to ensure
its code formatting. Please follow the documentation to
`install it <https://pre-commit.com/#installation>`_ and enable it in your
repository.

If you don't want to install it as a global system package, you can use a
`Python virtualenv <https://packaging.python.org/key_projects/#venv>`_ instead::

  python3 -m venv <virtualenv_folder>
  source <virtualenv_folder>/bin/activate
  pip install pre-commit
  pre-commit install

It will ensure, using git hook scripts, that your code respects the Flask-Inertia
code formatting guidelines.

Testing
-------

As mentioned before, it is very unlikely that we will accept code contributions
without the proper testing. There are two tests sets in Flask-Inertia concerning
respectively the Python codebase and the JavaScript codebase.

The Python codebase
^^^^^^^^^^^^^^^^^^^

The Python codebase use the standard `unitest` module to execute the tests cases,
and the `coverage tool <https://coverage.readthedocs.io/en/coverage-5.5/>`_ for
measuring the code coverage.

You can run these tests using the following commands::

  python3 -m venv tests_venv
  source ./tests_venv/bin/activate
  pip install coverage
  pip install -r requirements.txt
  coverage run --source=flask_inertia -m unittest tests.python.test_app
  coverage report -m --fail-under=90

Your Pull Request will not be accepted if the code coverage falls under 90%.

You can add your tests cases in the file `tests/python/test_app.py` adding new
cases to the existing `TestInertia` class or create a new class for your
purposes.

The JavaScript codebase
^^^^^^^^^^^^^^^^^^^^^^^

.. note::

   The JavaScript tests concerns exclusively the `flask_inertia/router.js` file.
   You should not modify these tests if your patch does not impact this file.

The JavaScript codebase use the `jest <https://jestjs.io/>`_ tool to execute its
test cases. You will need `nodejs` and `npm` installed to run these tests. A
Python script will be used to create the flask-inertia generated JavaScript.

You can run these tests as followed::

  python3 -m venv tests_venv
  source ./tests_venv/bin/activate
  python3 setup.py install
  python3 tests/js/setup.py
  npm install
  npm run test

You can add your tests cases in the file `tests/js/unit/test_router.spec.js`
adding new `it` methods for your purposes.


Commit messages
---------------

Each commit message consists of a header and an optional body. The header has a
special format that includes a type, a scope and a subject::

  <type>(<scope>): <subject>
  <BLANK LINE>
  <body>

The header is mandatory and the scope of the header is optional.

The available types are the following:

* `new`: a commit of the type *new* introduces a new feature to the codebase
  (this correlates with MINOR in Semantic Versioning).
* `chg`: a commit of the type *chg* introduces a refactoring of the codebase
* `fix`: a commit of the type *fix* introduces a bugfix of the codebase (this
  correlates with PATCH in Semantic Versioning).
* `doc`: a commit of the type *doc* introduces a modification of the documentation

Version and Changelog
---------------------

No modification of the `__version__` variable in the `flask_inertia/__init__.py`
file nor the Changelog file will be accepted.
