#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import unittest

from flask import Flask, redirect, url_for

sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from inertia.inertia import Inertia  # noqa: E402
from inertia.views import render_inertia  # noqa: E402


class TestConfig:

    TESTING = True
    INERTIA_VERSION = 1
    INERTIA_TEMPLATE = "base.html"


def index():
    return render_inertia("Index")


def users():
    return redirect(url_for("index"))


def partial_loading():
    return render_inertia(
        "Partial",
        props={"a": "a", "b": "b", "c": "c"},
    )


class TestInertia(unittest.TestCase):
    """Flask-Inertia tests."""

    def setUp(self):
        app = Flask(__name__, template_folder=".")
        app.config.from_object(TestConfig)
        app.add_url_rule("/", "index", index)
        app.add_url_rule(
            "/users/", "users", users, methods=["PUT", "DELETE", "PATCH"]
        )
        app.add_url_rule("/partial/", "partial", partial_loading)

        Inertia(app)

        self.client = app.test_client()

    def test_non_inertia_view(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"component", response.data)
        self.assertIn(b"props", response.data)
        self.assertIn(b"url", response.data)
        self.assertIn(b"version", response.data)
        self.assertFalse(response.is_json)

    def test_wrong_version(self):
        headers = {
            "X-Inertia": "true",
            "X-Requested-With": "XMLHttpRequest",
            "X-Inertia-Version": "1000",
        }
        response = self.client.get("/", headers=headers)
        self.assertEqual(response.status_code, 409)

    def test_request_modifiers(self):
        headers = {
            "X-Inertia": "true",
            "X-Requested-With": "XMLHttpRequest",
            "X-Inertia-Version": "1",
        }
        response = self.client.get("/", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json)

    def test_redirect_303_for_put_patch_delete_requests(self):
        response = self.client.put("/users/", data={})
        self.assertEqual(response.status_code, 303)

        response = self.client.delete("/users/")
        self.assertEqual(response.status_code, 303)

        response = self.client.patch("/users/", data={})
        self.assertEqual(response.status_code, 303)

    def test_partial_loading(self):
        response = self.client.get("/partial/")
        self.assertIn(b'"a": "a"', response.data)
        self.assertIn(b'"b": "b"', response.data)
        self.assertIn(b'"c": "c"', response.data)

        headers = {
            "X-Inertia": "true",
            "X-Inertia-Version": "1",
            "X-Requested-With": "XMLHttpRequest",
            "X-Inertia-Partial-Data": ["a"],
            "X-Inertia-Partial-Component": "Partial",
        }
        response = self.client.get("/partial/", headers=headers)
        self.assertIn(b'"a":"a"', response.data)
        self.assertNotIn(b'"b": "b"', response.data)
        self.assertNotIn(b'"c": "c"', response.data)

    def test_include_router(self):
        response = self.client.get("/")
        self.assertIn(
            b'window.routes = {"index": "/", "partial": "/partial/", "static": "/static/<path:filename>", "users": "/users/"}',
            response.data,
        )


if __name__ == "__main__":
    unittest.main()
