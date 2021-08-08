Flask-Inertia
=============

|coverage| |version| |inertiaversion| |license|


`Inertiajs <https://inertiajs.com/>`_ Adapter for `Flask <https://flask.palletsprojects.com/>`_.


Installation
------------

.. code-block:: bash

   $ pip install flask-inertia

Configuration
-------------

The module needs to be initialized the usual Flask way and can be configured using
``app.config`` keys::

  from flask import Flask
  from flask_inertia import Inertia

  SECRET_KEY = "secret!"
  # mandatory key
  INERTIA_TEMPLATE = "base.html"

  app = Flask(__name__)
  app.config.from_object(__name__)

  inertia = Inertia()
  inertia.init_app(app)
  # or inertia = Inertia(app)


The config key ``INERTIA_TEMPLATE`` must be used to set globally the template used by
``flask_inertia`` to render the server responses. This template must exists in the
Flask app ``templates`` folder.

Use
---

For more information about InertiaJS, please
`read the docs provided by Inertia <https://inertiajs.com/>`_.

Whereas the Rails and Laravel adapters use a middleware to manage Inertia's
requests, this module doesn't. Once it has been initiliazed it will create
``before_request`` and ``after_request`` hooks for your app to handle InertiaJS
frontend requests.

Your templates
++++++++++++++

You will need to setup the root template that will be loaded on the first page
visit. It will be used to load your site assets (CSS and JavaScript), and will
also contain a root ``<div>`` to boot your JavaScript application in.

.. code:: jinja

  <!DOCTYPE html>
  <html>
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0" />
      <title>My app</title>
      <link href="{{ url_for('static', filename='/css/app.css') }}" rel="stylesheet" />
      <script lang="javascript">
        {{ inertia.include_router() }}
      </script>
    </head>
    <body>
      <div id="app" data-page='{{ page | tojson }}'></div>
      <script src="{{ url_for('static', filename='/js/app.js') }}" defer></script>
    </body>
  </html>


.. warning:: Be aware of the single quotes used for the ``data-page`` argument.
   Jinja2 will not escape the double quotes of your JSON object
   https://github.com/pallets/flask/issues/1002

Your root ``div`` must set a HTML ``data-page`` attribute. It will be used by Flask,
using a `Page JSON object <https://inertiajs.com/the-protocol#the-page-object>`_
to communicate with Inertia.

To facilitate the route path resolving, the module provide a template context method
called ``inertia.include_router``. It will expose the Flask views resolution (like
the ``url_for`` method) to your frontend Components.

This method has been extracted to `django-js-routes <https://github.com/ellmetha/django-js-routes>`_
package and works the same way via a ``window.reverseUrl`` JavaScript method (
https://github.com/ellmetha/django-js-routes#usage).

Create responses
++++++++++++++++

This module provides a method ``render_inertia`` to render your frontend component
through Flask responses. It will wrap your Responses and act accordingly to Inertia
requests context responding a full html or a JSON reponse. It will be used instead
of Flask ``render_template`` method::

  from flask_inertia import render_inertia

  @app.route("/test_inertia/")
  def test_inertia():
      """An endpoint to test inertia integration."""
      data = {
          "username": "foo",
          "login": "bar",
      }
      return render_inertia(
          component_name="Index",
          props=data,
      )

This method take 2 arguments:

  * ``component_name``: Your frontend component name (eg "Index" for an Index.vue
    Component for example)
  * ``props``: [OPTIONAL] Data used by your component


Share data between requests
+++++++++++++++++++++++++++

Sometimes you need to access certain data on numerous pages within your application.
For example, a common use-case for this is showing the current user in the site
header. Passing this data manually in each response isn't practical. In these
situations shared data can be useful.

This module provides a ``share`` method into the ``Inertia`` class to preassign
shared data for each request. Shared data will be automatically merged with the
page ``props`` provided in your controller. It takes as argument a key/value pair
to serialize it in JSON in the responses.

You can set the shared data statically or programmatically using the method as
followed::

  inertia = Inertia(app)

  # set statically a shared data
  inertia.share("foo", "bar")

  # or a computed value
  def shared_value():
      return "buzz"

  inertia.share("fizz", shared_value)

If the value is a ``callable``, the module will resolve it during the response
resolution.

To see a complete exemple on how to implement a project with this adapter, please
read our `Tutorial <https://flask-inertia.readthedocs.io/en/latest/tutorial.html>`_.

Contributing
------------

If you want to contribute to this project, please read the dedicated file :
`CONTRIBUTING.rst`.


.. |coverage| image:: https://git.joakode.fr/joack/flask-inertia/badges/main/coverage.svg
.. |version| image:: https://img.shields.io/pypi/v/flask-inertia.svg
.. |license| image:: https://img.shields.io/github/license/j0ack/flask-inertia.svg
.. |inertiaversion| image:: https://img.shields.io/badge/inertia-0.10.1-cyan
