============
App skeleton
============

First let's create the app skeleton:

.. code:: bash

  .
  |-- Makefile
  |-- README.md
  |-- app.py
  |-- static
  |   |-- dist
  |   `-- vue
  |-- templates
  |   `-- base.html


The ``app.py`` file is a simple single file Flask application using as arguments
the ``templates`` directory as ``template_folder`` and ``static/dist`` as
``static_folder``.

The ``static/vue`` store the frontend application powered by Vue3/Inertia. Vue
generates a JavaScript file on build named ``main.js``. It will be configured to
generate this files in our ``static/dist`` folder to be available for our Flask
application.

Since, there are going to be two different applications (Python and Vue), a
``Makefile`` will be used to run the parallel build and provide a ``hot-reload``
development environment.

Automate development environment
================================

To run the application in development mode two processes needs to executed:

* A Flask process running the app in development mode
* A Vue build process watching for any changes in the code source files

For more convenience, a Makefile will be used to run these processes in parallel
with a single command. Implement the Makefile present in your project root folder
as followed:

.. code:: Makefile

   # use parallel tasks
   MAKEFLAGS+="-j 2"

   .PHONY: all
   all: dev

   # run Flask app in development mode
   dev-python:
          FLASK_APP=app:app FLASK_DEBUG=1 flask run

   # build Vue app in development mode with hot-reload
   # this build will be covered in the client-side part
   dev-vue:
          @npm run --prefix static/vue/ build:dev

   # run development environment
   dev: dev-python dev-vue

Then, run ``make dev`` to run your development environment.
