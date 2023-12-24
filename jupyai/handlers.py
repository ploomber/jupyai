import json
from http import HTTPStatus

from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
import tornado

from jupyai import autocomplete, exceptions


class RouteHandler(APIHandler):
    # The following decorator should be present on all verb methods (head, get, post,
    # patch, put, delete, options) to ensure only authorized user can request the
    # Jupyter server
    @tornado.web.authenticated
    def post(self):
        body = self.get_json_body()

        try:
            output = autocomplete.autocomplete(
                body["cell"],
                body["sources"],
            )
        except exceptions.UnauthorizedException as e:
            raise tornado.web.HTTPError(
                HTTPStatus.UNAUTHORIZED.value, "Missing OpenAI API key"
            ) from e

        self.finish(json.dumps({"data": output}))


def setup_handlers(web_app):
    host_pattern = ".*$"

    base_url = web_app.settings["base_url"]
    handlers = [(url_path_join(base_url, "jupyai", "autocomplete"), RouteHandler)]
    web_app.add_handlers(host_pattern, handlers)
