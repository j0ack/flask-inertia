Unit tests
==========

Flask-Inertia provides an extra module to facilitate testing using a custom
`Response <https://flask.palletsprojects.com/en/2.1.x/api/#flask.Response>`_ class.
It handles Inertia response context for you to get the data either stored in the
HTML attribute or as a JSON object. You can then use it with your favorite testing
solution.

Installation
------------

Flask-Inertia uses the `BeautifulSoup <https://pypi.org/project/beautifulsoup4/>`_
library to parse the HTML and extract the page JSON object. Since it is not a
core dependency it is listed as a `tests extra requirement`. You can install it
as followed:

.. code-block:: bash

  $ pip install flask-inertia[tests]


Use
---

Flask gives the option to replace the response class with a custom one using the
application object attribute `response_class`. Knowing that, you can customize your
test cases response using the provided `InertiaTestResponse` class.

It exposes an `inertia` method to access the Inertia data in response.

You can configure a `TestCase` as followed:

.. code-block:: python

  import unittest

  from inertia.unittest import InertiaTestResponse

  from myapp import create_app


  class MyTestCase(unittest.TestCase):

      def setUp(self):
          self.app = create_app()  # if you use an application factory
          self.app.response_class = InertiaTestResponse
          self.client = self.app.test_client()


Test Inertia data
+++++++++++++++++

The `inertia` method parse either the flask HTML response, to extract the JSON
encoded inertia page object, or the JSON response based on its headers.

It converts the page JSON object into a Python object using
`SimpleNamespace <https://docs.python.org/3/library/types.html#types.SimpleNamespace>`_.

For this example, the tests will cover the index `view` defined in the :doc:`tutorial`
part.

.. code-block:: python

  import unittest

  from inertia.unittest import InertiaTestResponse

  from app import app


  class TestIndex(unittest.TestCase):

      def setUp(self):
          self.app = app
          self.app.response_class = InertiaTestResponse
          self.client = self.app.test_client()

      def test_inertia_component(self):
          response = self.client.get("/")
          data = response.inertia("app")
          self.assertEqual(data.component, "Index")

      def test_inertia_props(self):
          response = self.client.get("/")
          data = response.inertia("app")
          self.assertEqual(data.props.foo, "bar")
          self.assertEqual(data.props.fiz, "buzz")
          self.assertEqual(data.props.num, 42)

      def test_inertia_json_response(self):
          response = self.client.get(
              "/",
              headers={"X-Inertia": True}
          )
          data = response.inertia("app")
          self.assertEqual(data.component, "Index")
