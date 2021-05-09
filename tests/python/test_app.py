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

import re
import unittest
from unittest.mock import patch

from flask import Flask, redirect, url_for

from flask_inertia import Inertia, render_inertia


class TestConfig:

    TESTING = True
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
        self.app = Flask(__name__, template_folder=".")
        self.app.config.from_object(TestConfig)
        self.app.add_url_rule("/", "index", index)
        self.app.add_url_rule(
            "/users/", "users", users, methods=["PUT", "DELETE", "PATCH"]
        )
        self.app.add_url_rule("/partial/", "partial", partial_loading)

        self.inertia = Inertia(self.app)

        self.client = self.app.test_client()

    def test_extension_init(self):
        app = Flask(__name__, template_folder=".")
        app.config.from_object(TestConfig)
        # remove extensions attr
        del app.extensions

        Inertia(app)
        self.assertIsNotNone(app.extensions)
        self.assertIn("inertia", app.extensions)

    def test_bad_request(self):
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "X-Inertia-Version": "1000",
        }
        response = self.client.get("/", headers=headers)
        self.assertEqual(response.status_code, 400)

    def test_no_inertia_template(self):
        del self.app.config["INERTIA_TEMPLATE"]
        response = self.client.get("/")
        self.assertEqual(response.status_code, 400)

    def test_non_inertia_view(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"component", response.data)
        self.assertIn(b"props", response.data)
        self.assertIn(b"url", response.data)
        self.assertIn(b"version", response.data)
        self.assertIn(b"http://localhost/", response.data)
        self.assertFalse(response.is_json)

    def test_wrong_version(self):
        with patch("flask_inertia.inertia.get_asset_version") as get_version_mock:
            get_version_mock.return_value = "1"
            headers = {
                "X-Inertia": "true",
                "X-Requested-With": "XMLHttpRequest",
                "X-Inertia-Version": "1000",
            }
            response = self.client.get("/", headers=headers)
            self.assertEqual(response.status_code, 409)

    def test_request_modifiers(self):
        with patch("flask_inertia.inertia.get_asset_version") as get_version_mock:
            get_version_mock.return_value = "1"
            headers = {
                "X-Inertia": "true",
                "X-Requested-With": "XMLHttpRequest",
                "X-Inertia-Version": "1",
            }
            response = self.client.get("/", headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"http://localhost/", response.data)
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
        self.assertIn(b"http://localhost/partial/", response.data)

        version_match = re.search(
            r'"version": "[A-Fa-f0-9]{64}"', response.data.decode("utf-8")
        ).group()
        assert version_match is not None
        version = version_match.split(": ")[1].replace('"', "")

        headers = {
            "X-Inertia": "true",
            "X-Inertia-Version": version,
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
            b'window.routes={"index":"/","partial":"/partial/","static":"/static/<path:filename>","users":"/users/"}',
            response.data,
        )

    def test_share_values(self):
        self.inertia.share("foo", "bar")
        response = self.client.get("/")
        self.assertIn(b'"foo": "bar"', response.data)

    def test_share_computed_values(self):
        def shared_data():
            return "buzz"

        self.inertia.share("fizz", shared_data)
        response = self.client.get("/")
        self.assertIn(b'"fizz": "buzz"', response.data)

    def test_not_duplicated_shared_value_in_props(self):
        self.inertia.share("e", "shared_data")
        response = self.client.get("/partial/")
        self.assertIn(b'"e": "shared_data"', response.data)
        response = self.client.get("/partial/")
        self.assertIn(b'"e": "shared_data"', response.data)
        self.assertNotIn(b"shared_e", response.data)


if __name__ == "__main__":
    unittest.main()
