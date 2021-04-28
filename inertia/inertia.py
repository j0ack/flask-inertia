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
from typing import Optional

from flask import Flask, Markup, Response, current_app, request
from jinja2 import Template
from werkzeug.exceptions import BadRequest


class Inertia:
    """Inertia Plugin for Flask."""

    def __init__(self, app: Optional[Flask] = None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        """Init app, register request hooks and set context processor."""
        if not hasattr(app, "extensions"):
            app.extensions = {}
        app.extensions["inertia"] = self
        app.context_processor(self.context_processor)
        app.config.setdefault("INERTIA_VERSION", "1")
        app.before_request(self._check_inertia)
        app.after_request(self._modify_response)

    def _check_inertia(self) -> Optional[Response]:
        """Check Inertia requests."""
        # request is ajax
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            # check if send with Inertia
            if not request.headers.get("X-Inertia"):
                raise BadRequest("Inertia headers not found")

            # check inertia version
            inertia_version = current_app.config.get("INERTIA_VERSION", "1")
            inertia_version_header = request.headers.get("X-Inertia-Version")
            if inertia_version_header and inertia_version_header != str(
                inertia_version
            ):
                response = Response("Inertia versions does not match", status=409)
                response.headers["X-Inertia-Location"] = request.full_path
                return response

        return None

    def _modify_response(self, response: Response) -> Response:
        if (
            request.method in ["PUT", "PATCH", "DELETE"]
            and response.status_code == 302
        ):
            response.status_code = 303

        return response

    @staticmethod
    def context_processor():
        return {
            "inertia": current_app.extensions["inertia"],
        }

    def include_router(self) -> Markup:
        """Include JS router in Templates."""
        router_file = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "router.js"
        )
        routes = {
            rule.endpoint: rule.rule for rule in current_app.url_map.iter_rules()
        }
        with open(router_file, "r") as jsfile:
            template = Template(jsfile.read())
            # Jinja2 template automatically get rid of ['<'|'>'] chars
            content = (
                template.render(routes=routes)
                .replace("\\u003c", "<")
                .replace("\\u003e", ">")
            )

        return Markup(content)
