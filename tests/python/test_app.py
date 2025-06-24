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
from http import HTTPStatus
from unittest.mock import patch

from flask import Blueprint, Flask, redirect, url_for
from parameterized import parameterized

from flask_inertia import (
    Inertia,
    always_include,
    inertia_location,
    lazy_include,
    render_inertia,
)
from flask_inertia.unittest import InertiaTestResponse


class TestConfig:

    TESTING = True
    INERTIA_TEMPLATE = "base.html"


def index():
    return render_inertia("Index")


def users():
    return redirect(url_for("index"))


def external():
    return inertia_location("http://foobar.com/")


def a() -> str:
    return "a"


def b() -> str:
    return "b"


def c() -> str:
    return "c"


def d() -> str:
    return "d"


def partial_loading():
    return render_inertia(
        "Partial",
        props={
            "a": a(),
            "b": b,
            "c": lazy_include(c),
            "d": always_include(d()),
        },
    )


def meta():
    return render_inertia(
        "Meta",
        props={"a": "a", "b": "b", "c": "c", "foo": "bar"},
        view_data={"description": "A test page"},
    )


class TestInertia(unittest.TestCase):
    """Flask-Inertia tests."""

    def setUp(self):
        self.app = Flask(__name__, template_folder=".")
        self.app.config.from_object(TestConfig)
        self.app.add_url_rule("/", "index", index)
        self.app.add_url_rule("/external/", "external", external)
        self.app.add_url_rule(
            "/users/", "users", users, methods=["PUT", "DELETE", "PATCH"]
        )
        self.app.add_url_rule("/partial/", "partial", partial_loading)
        self.app.add_url_rule("/meta/", "meta", meta)

        self.inertia = Inertia(self.app)
        self.inertia.add_shorthand_route("/faq/", "FAQ")
        self.inertia.add_shorthand_route("/about/", "About", "about page")

        self.client = self.app.test_client()

    def test_extension_init(self):
        app = Flask(__name__, template_folder=".")
        app.config.from_object(TestConfig)
        # remove extensions attr
        del app.extensions

        Inertia(app)
        self.assertIsNotNone(app.extensions)
        self.assertIn("inertia", app.extensions)

    def test_bad_extension_init(self):
        inertia = Inertia()
        with self.assertRaises(RuntimeError) as ctx:
            inertia.add_shorthand_route("/faq/", "FAQ")

        self.assertIn(
            "Extension has not been initialized correctly", str(ctx.exception)
        )

    def test_bad_request(self):
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "X-Inertia-Version": "1000",
        }
        response = self.client.get("/", headers=headers)
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_no_inertia_template(self):
        del self.app.config["INERTIA_TEMPLATE"]
        response = self.client.get("/")
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_non_inertia_view(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, HTTPStatus.OK)
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
            self.assertEqual(response.status_code, HTTPStatus.CONFLICT)

    def test_request_modifiers(self):
        with patch("flask_inertia.inertia.get_asset_version") as get_version_mock:
            get_version_mock.return_value = "1"
            headers = {
                "X-Inertia": "true",
                "X-Requested-With": "XMLHttpRequest",
                "X-Inertia-Version": "1",
            }
            response = self.client.get("/", headers=headers)
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertIn(b"http://localhost/", response.data)
            self.assertTrue(response.is_json)

    def test_redirect_303_for_put_patch_delete_requests(self):
        response = self.client.put("/users/", data={})
        self.assertEqual(response.status_code, HTTPStatus.SEE_OTHER)

        response = self.client.delete("/users/")
        self.assertEqual(response.status_code, HTTPStatus.SEE_OTHER)

        response = self.client.patch("/users/", data={})
        self.assertEqual(response.status_code, HTTPStatus.SEE_OTHER)

    def test_invalid_lazy_include_type(self):
        with self.assertRaises(ValueError):
            dict(test=lazy_include("not a callable"))

    @parameterized.expand(
        [
            ("a", True, False, False, True),
            ("a,c", True, False, True, True),
            ("b,c", False, True, True, True),
        ]
    )
    def test_partial_loading_with_multiple_partial_data_headers(
        self, header, a_data, b_data, c_data, d_data
    ):
        with (
            patch("tests.python.test_app.a") as a_mock,
            patch("tests.python.test_app.b") as b_mock,
            patch("tests.python.test_app.c") as c_mock,
            patch("tests.python.test_app.d") as d_mock,
        ):
            a_mock.return_value = "a"
            b_mock.return_value = "b"
            c_mock.return_value = "c"
            d_mock.return_value = "d"

            # standard visite
            response = self.client.get("/partial/")
            self.assertIn(b'"a": "a"', response.data)
            self.assertIn(b'"b": "b"', response.data)
            self.assertNotIn(b'"c": "c"', response.data)
            self.assertIn(b'"d": "d"', response.data)
            self.assertIn(b"http://localhost/partial/", response.data)

            self.assertTrue(a_mock.called)
            self.assertTrue(b_mock.called)
            self.assertFalse(c_mock.called)
            self.assertTrue(d_mock.called)

        with (
            patch("tests.python.test_app.a") as a_mock,
            patch("tests.python.test_app.b") as b_mock,
            patch("tests.python.test_app.c") as c_mock,
            patch("tests.python.test_app.d") as d_mock,
        ):
            a_mock.return_value = "a"
            b_mock.return_value = "b"
            c_mock.return_value = "c"
            d_mock.return_value = "d"

            version_match = re.search(
                r'"version": "[A-Fa-f0-9]{64}"', response.data.decode("utf-8")
            ).group()
            assert version_match is not None
            version = version_match.split(": ")[1].replace('"', "")

            headers = {
                "X-Inertia": "true",
                "X-Inertia-Version": version,
                "X-Requested-With": "XMLHttpRequest",
                "X-Inertia-Partial-Data": [header],
                "X-Inertia-Partial-Component": "Partial",
            }

            response = self.client.get("/partial/", headers=headers)
            self.assertEqual(b'"a":"a"' in response.data, a_data)
            self.assertEqual(a_mock.called, True)
            self.assertEqual(b'"b":"b"' in response.data, b_data)
            self.assertEqual(b_mock.called, b_data)
            self.assertEqual(b'"c":"c"' in response.data, c_data)
            self.assertEqual(c_mock.called, c_data)
            self.assertEqual(b'"d":"d"' in response.data, d_data)
            self.assertEqual(d_mock.called, True)

    def test_partial_loading_with_comma_separated_props_in_partial_data_header(self):
        response = self.client.get("/partial/")
        self.assertIn(b'"a": "a"', response.data)
        self.assertIn(b'"b": "b"', response.data)
        self.assertNotIn(b'"c": "c"', response.data)
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
            "X-Inertia-Partial-Data": ["a,b"],
            "X-Inertia-Partial-Component": "Partial",
        }
        response = self.client.get("/partial/", headers=headers)
        self.assertIn(b'"a":"a"', response.data)
        self.assertIn(b'"b":"b"', response.data)

        self.assertNotIn(b'"c": "c"', response.data)
        self.assertIn(b'"d":"d"', response.data)

    def test_include_router(self):
        response = self.client.get("/")
        self.assertIn(
            b'window.routes={"about page":"/about/","external":"/external/","faq":"/faq/","index":"/","meta":"/meta/","partial":"/partial/","static":"/static/<path:filename>","users":"/users/"}',
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

    def test_page_meta(self):
        response = self.client.get("/meta/")
        self.assertIn(b'<meta name="author" content="bar">', response.data)
        self.assertIn(
            b'<meta name="description" content="A test page">', response.data
        )

    def test_backend_redirect(self):
        response = self.client.get("/external/")
        self.assertEqual(response.status_code, HTTPStatus.CONFLICT)
        self.assertEqual(b"Inertia server side redirect", response.data)
        self.assertIn("X-Inertia-Location", response.headers)
        self.assertEqual(
            "http://foobar.com/", response.headers["X-Inertia-Location"]
        )

    def test_shorthand_route(self):
        response = self.client.get("/faq/")
        self.assertEqual(response.status_code, HTTPStatus.OK)


class TestInertiaTestUtils(unittest.TestCase):
    """Flask-Inertia tests."""

    def setUp(self):
        self.app = Flask(__name__, template_folder=".")
        self.app.config.from_object(TestConfig)
        self.app.add_url_rule("/", "index", index)
        self.app.add_url_rule(
            "/users/", "users", users, methods=["PUT", "DELETE", "PATCH"]
        )
        self.app.add_url_rule("/partial/", "partial", partial_loading)
        self.app.add_url_rule("/meta/", "meta", meta)

        self.inertia = Inertia(self.app)
        self.inertia.add_shorthand_route("/faq/", "FAQ")

        self.app.response_class = InertiaTestResponse
        self.client = self.app.test_client()

    def test_partial_loading(self):
        response = self.client.get("/partial/")
        data = response.inertia("app")
        self.assertEqual(data.props.a, "a")
        self.assertEqual(data.props.b, "b")
        self.assertEqual(data.props.d, "d")
        self.assertEqual(data.url, "http://localhost/partial/")

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
        data = response.inertia("app")
        self.assertEqual(data.props.a, "a")
        self.assertFalse(hasattr(data.props, "b"))
        self.assertFalse(hasattr(data.props, "c"))

    def test_share_values(self):
        self.inertia.share("foo", "bar")
        response = self.client.get("/")
        data = response.inertia("app")
        self.assertEqual(data.props.foo, "bar")

    def test_share_computed_values(self):
        def shared_data():
            return "buzz"

        self.inertia.share("fizz", shared_data)
        response = self.client.get("/")
        data = response.inertia("app")
        self.assertEqual(data.props.fizz, "buzz")

    def test_import_error(self):
        import builtins

        realimport = builtins.__import__

        # replace builtins import with a mockup raising an ImportError
        # when import BeautifulSoup
        def mockupimport(name, *args, **kwargs):
            if name == "bs4":
                raise ImportError("Test")
            return realimport(name, *args, **kwargs)

        builtins.__import__ = mockupimport
        response = self.client.get("/")
        with self.assertRaises(ImportError) as exc:
            response.inertia("app")

        self.assertIn(
            "flask-inertia needs BeautifulSoup to parse html messages",
            exc.exception.msg,
        )
        self.assertIn(
            "please install it using `pip install flask-inertia[tests]`",
            exc.exception.msg,
        )

        builtins.__import__ = realimport

    def view_data_not_in_js_context(self):
        response = self.client.get("/meta/")
        data = response.inertia("app")
        self.assertFalse(hasattr(data.props, "description"))

    def test_shorthand_route(self):
        response = self.client.get("/faq/")
        data = response.inertia("app")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(data.component, "FAQ")


class TestBlueprint(unittest.TestCase):
    """Flask-Inertia blueprint tests."""

    def setUp(self):
        self.blueprint = Blueprint("inertia", __name__, template_folder=".")
        self.blueprint.add_url_rule("/", "index", index)

        self.inertia = Inertia(self.blueprint)
        self.inertia.add_shorthand_route("/faq/", "FAQ")

        self.app = Flask(__name__, template_folder=".")
        self.app.config.from_object(TestConfig)
        self.app.register_blueprint(self.blueprint)

        self.app.response_class = InertiaTestResponse
        self.client = self.app.test_client()

    def test_extension_registered(self):
        self.assertIn("inertia", self.app.extensions)

    def test_shorthand_route(self):
        response = self.client.get("/faq/")
        data = response.inertia("app")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(data.component, "FAQ")


if __name__ == "__main__":
    unittest.main()
