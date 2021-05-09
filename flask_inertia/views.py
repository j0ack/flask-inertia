#!/usr/bin/env python
# -*- coding: utf-8 -*-

# MIT License
#
# Copyright (c) 2021 TROUVERIE Joachim <jtrouverie@joakode.fr>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
flask_inertia.views
-------------------

Implement a method to add Inertia rendering into Flask.
"""

from flask import Response, abort, current_app, jsonify, render_template, request

from flask_inertia.version import get_asset_version


def render_inertia(component_name: str, props: dict = {}) -> Response:
    """Method to use instead of Flask `render_template`.

    Returns either a JSON response or a HTML response including a JSON encoded inertia
    page object according to Inertia request headers.

    .. code-block:: python

       from flask_inertia import render_inertia

       app = Flask(__name__)

       @app.route("/")
       def index():
           data = {
               "username": "foo",
               "login": "bar",
           }
           return render_inertia(
               component_name="Index",  # this must exists in your frontend
               props=data,  # optional
           )

    :param component_name: The component name used in your frontend framework
    :param props: A dict of properties used in your component
    """
    inertia_template = current_app.config.get("INERTIA_TEMPLATE")
    if inertia_template is None:
        abort(
            400,
            "No Inertia template found. Set INERTIA_TEMPLATE in config",
        )

    inertia_version = get_asset_version()
    refresh_props = request.headers.getlist("X-Inertia-Partial-Data")
    if (
        refresh_props
        and request.headers.get("X-Inertia-Partial-Component", "") == component_name
    ):
        props = {key: value for key, value in props.items() if key in refresh_props}

    extension = current_app.extensions["inertia"]
    for key, value in extension._shared_data.items():
        if callable(value):
            props[key] = value()
        else:
            props[key] = value

    if request.headers.get("X-Inertia", False):
        response = jsonify(
            {
                "component": component_name,
                "props": props,
                "version": inertia_version,
                "url": request.url,
            }
        )
        response.headers["X-Inertia"] = True
        response.headers["Vary"] = "Accept"
        return response

    context = {
        "page": {
            "version": inertia_version,
            "url": request.url,
            "component": component_name,
            "props": props,
        },
    }

    return render_template(inertia_template, **context)
