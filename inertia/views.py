from typing import Optional

from flask import (
    abort,
    request,
    jsonify,
    Response,
    current_app,
    render_template,
)


def render_inertia(
    component_name: str, props: dict = {}, template_name: Optional[str] = None
) -> Response:
    inertia_version = current_app.config.get("INERTIA_VERSION")
    inertia_template = current_app.config.get("INERTIA_TEMPLATE", template_name)
    if inertia_template is None:
        return abort(
            400,
            "No Inertia template found. Either set INERTIA_TEMPLATE"
            + "in config or pass template parameter.",
        )

    refresh_props = request.headers.getlist("X-Inertia-Partial-Data")
    if (
        refresh_props
        and request.headers.get("X-Inertia-Partial-Component", "") == component_name
    ) :
        props = {
            key: value for key, value in props.items() if key in refresh_props
        }

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
