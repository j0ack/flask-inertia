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

from typing import Optional

from flask import Response, abort, current_app, jsonify, render_template, request

from flask_inertia.version import get_asset_version


def render_inertia(
    component_name: str, props: dict = {}, template_name: Optional[str] = None
) -> Response:
    """Method to use instead of Flask `render_template`."""
    inertia_version = get_asset_version()
    inertia_template = template_name or current_app.config.get("INERTIA_TEMPLATE")
    if inertia_template is None:
        abort(
            400,
            "No Inertia template found. Either set INERTIA_TEMPLATE"
            + "in config or pass template parameter.",
        )

    refresh_props = request.headers.getlist("X-Inertia-Partial-Data")
    if (
        refresh_props
        and request.headers.get("X-Inertia-Partial-Component", "") == component_name
    ):
        props = {key: value for key, value in props.items() if key in refresh_props}

    if request.headers.get("X-Inertia", False):
        response = jsonify(
            {
                "component": component_name,
                "props": props,
                "version": inertia_version,
                "url": request.full_path,
            }
        )
        response.headers["X-Inertia"] = True
        response.headers["Vary"] = "Accept"
        return response

    context = {
        "page": {
            "version": inertia_version,
            "url": request.full_path,
            "component": component_name,
            "props": props,
        },
    }

    return render_template(inertia_template, **context)
