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

from flask_inertia.version import get_asset_version


class Inertia:
    """Inertia Plugin for Flask."""

    def __init__(self, app: Optional[Flask] = None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        """Init as an app extension

        * Register before_request hook
        * Register after_request hook
        * Set context processor to have an `inertia` value in templates
        """
        if not hasattr(app, "extensions"):
            app.extensions = {}
        app.extensions["inertia"] = self
        app.context_processor(self.context_processor)
        app.before_request(self.process_incoming_inertia_requests)
        app.after_request(self.update_redirect)

    def process_incoming_inertia_requests(self) -> Optional[Response]:
        """Process incoming Inertia requests.

        AJAX requests must be forged by Inertia.

        Whenever an Inertia request is made, Inertia will include the current asset
        version in the X-Inertia-Version header. If the asset versions are the same,
        the request simply continues as expected. However, if they are different,
        the server immediately returns a 409 Conflict response (only for GET request),
        and includes the URL in a X-Inertia-Location header.
        """
        # request is ajax
        if request.headers.get("X-Requested-With") != "XMLHttpRequest":
            return None

        # check if send with Inertia
        if not request.headers.get("X-Inertia"):
            raise BadRequest("Inertia headers not found")

        # check inertia version
        server_version = get_asset_version()
        inertia_version = request.headers.get("X-Inertia-Version")
        if (
            request.method == "GET"
            and inertia_version
            and inertia_version != str(server_version)
        ):
            response = Response("Inertia versions does not match", status=409)
            response.headers["X-Inertia-Location"] = request.full_path
            return response

        return None

    def update_redirect(self, response: Response) -> Response:
        """Update redirect to set 303 status code.

        409 conflict responses are only sent for GET requests, and not for
        POST/PUT/PATCH/DELETE requests. That said, they will be sent in the
        event that a GET redirect occurs after one of these requests. To force
        Inertia to use a GET request after a redirect, the 303 HTTP status is used
        """
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
