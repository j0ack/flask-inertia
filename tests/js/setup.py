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
Create setup for JS tests
"""

import os

from flask import Flask

from flask_inertia import Inertia

CURDIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
inertia = Inertia(app)


@app.route("/")
def route_without_arg():
    pass


@app.route("/<user_id>/")
def route_with_arg(user_id):
    pass


@app.route("/<int:user_id>/")
def route_with_typed_arg(user_id):
    pass


@app.route("/<account_id>/<user_id>/")
def route_with_multiple_args(account_id, user_id):
    pass


with app.app_context():
    jsroutes = inertia.include_router()
    with open(os.path.join(CURDIR, "resolver.js"), "w+") as libfile:
        libfile.write(jsroutes)
