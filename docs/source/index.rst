
.. image:: _static/logo.png
   :align: center


Welcome to Flask-Inertia's documentation
========================================

|coverage| |version| |inertiaversion| |license|

`Inertiajs <https://inertiajs.com/>`_ Adapter for `Flask <https://flask.palletsprojects.com/>`_.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   tutorial
   unittest
   api


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

  from flask.typing import ResponseReturnValue
  from flask_inertia import render_inertia

  @app.route("/test_inertia/")
  def test_inertia() -> ResponseReturnValue:
      """An endpoint to test inertia integration."""
      data = {
          "username": "foo",
          "login": "bar",
      }
      return render_inertia(
          component_name="Index",
          props=data,
          view_data={},
      )

This method take 3 arguments:

  * ``component_name``: Your frontend component name (e.g. "Index" for an Index.vue
    Component for example)
  * ``props``: [OPTIONAL] Data used by your component
  * ``view_data``: [OPTIONAL] Data used in your template but not sent to your JavaScript
    components

Shorthand routes
++++++++++++++++

If you have a page that does not need a corresponding controller method (i.e. a frontend
component which does not need ``props`` nor ``view_data``), like a "FAQ" or "about" page,
you can route directly to a component via the ``add_shorthand_route`` method::

  from flask import Flask
  from flask_inertia import Inertia

  app = Flask(__name__)
  app.config.from_object(__name__)
  inertia = Inertia(app)

  inertia.add_shorthand_route("/faq/", "FAQ")
  inertia.add_shorthand_route("/about/", "About", "My About Page")


This method takes 3 arguments:

  * ``url``: The URL rule as string as used in ``flask.add_url_rule``
  * ``component_name``: Your frontend component name (e.g. "Index" for an Index.vue
    Component for example)
  * ``endpoint`` [OPTIONAL]: The endpoint for the registered URL rule. (by default the
    ``component_name`` in lower case)

Root template data
++++++++++++++++++

There are situations where you may want to access your prop data in your root Jinja2
template. These props are available via the ``page`` variable.

.. code:: jinja

   <meta name="author" content="{{ page['props']['username'] }}">

You may want to provide data that will not be sent to your JavaScript components.
You can do this using the ``view_data`` dictionnary in the ``render_inertia`` method::

  return render_inertia(
      component_name="Index",
      props=data,
      view_data={
          "description": "A test page"
      }
  )

You can then access this variable with the template variable ``view_data``.

.. code:: jinja

   <meta name="content" content="{{ view_data['description'] }}">

External redirects
++++++++++++++++++

It is possible to redirect to an external website, or even another non-Inertia endpoint
in your app while handling an Inertia request. This can be accomplished using a
server-side initiated ``window.location`` visit via the ``inertia_location`` method::

  from flask.typing import ResponseReturnValue
  from flask_inertia import inertia_location

  @app.route("/test_inertia/")
  def external_url() -> ResponseReturnValue:
      return inertia_location("http://foobar.com/")


It will generate a ``409 Conflict`` response and include the destination URL in
the ``X-Inertia-Location`` header. When this response is received client-side,
Inertia will automatically perform a ``window.location = url`` visit.

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
  def shared_value() -> str:
      return "buzz"

  inertia.share("fizz", shared_value)

If the value is a ``callable``, the module will resolve it during the response
resolution.

Lazy data evaluation
++++++++++++++++++++

When making visits to the same page you are already on, it's not always necessary
to re-fetch all of the page's data from the server. In fact, selecting only a subset
of the data can be a helpful performance optimization if it's acceptable that
some page data becomes stale.

For partial reloads to be most effective, be sure to also use lazy data evaluation
when returning props from your server-side routes or controllers. This can be
accomplished by wrapping all optional page data in a ``callable``::

  from flask.typing import ResponseReturnValue
  from flask_inertia import render_inertia

  def get_users() -> list[User]:
      return User.query.all()

  @app.route("/users/")
  def users_view() -> ResponseReturnValue:
      return render_inertia(
          "Users",
          props={
              "users": get_users,
              "companies": Company.query.all(),
          }
      )

When Inertia performs a request, it will determine which data is required and only
then will it evaluate the callable. This can significantly increase the performance
of pages that contain a lot of optional data.

Additionally, this module provides an ``lazy_include`` method to specify that a prop
should never be included unless explicitly requested using the ``only`` option. And
on the inverse, you can use the ``always_include`` method to specify that a prop
should always be included, even if it has not been explicitly required in a partial
reload::

  from flask.typing import ResponseReturnValue
  from flask_inertia import always_include, lazy_include, render_inertia

  def get_users() -> list[User]:
      return User.query.all()


  @app.route("/users/")
  def users_view() -> ResponseReturnValue:
      return render_inertia(
          "Users",
          props={
              # ALWAYS included on standard visits
              # OPTIONALLY included on partial reloads
              # ALWAYS evaluated
              "users": User.query.all(),  # or get_users()

              # ALWAYS included on standard visits
              # OPTIONALLY included on partial reloads
              # ONLY evaluated when needed
              "users": get_users,

              # NEVER included on standard visits
              # OPTIONALLY included on partial reloads
              # ONLY evaluated when needed
              "users": lazy_include(get_users),

              # ALWAYS included on standard visits
              # ALWAYS included on partial reloads
              # ALWAYS evaluated
              "users": always_include(User.query.all()),  # or always_include(get_users())
          }
      )

To see a complete exemple on how to implement a project with this adapter, please
read our :doc:`tutorial` or check this `demo project <https://github.com/j0ack/pingcrm-flask>`_.


.. |coverage| image:: https://git.joakode.fr/joack/flask-inertia/badges/main/coverage.svg
.. |version| image:: https://img.shields.io/pypi/v/flask-inertia.svg
.. |license| image:: https://img.shields.io/github/license/j0ack/flask-inertia.svg
.. |inertiaversion| image:: https://img.shields.io/badge/inertia-1.2-cyan
