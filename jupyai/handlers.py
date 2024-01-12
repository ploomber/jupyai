import json
from http import HTTPStatus
import logging


from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
import tornado

from jupyai import autocomplete, exceptions


logger = logging.getLogger(__name__)


class RouteHandler(APIHandler):
    # The following decorator should be present on all verb methods (head, get, post,
    # patch, put, delete, options) to ensure only authorized user can request the
    # Jupyter server
    @tornado.web.authenticated
    def post(self):
        body = self.get_json_body()

        logger.debug("Received request: %s", body)

        try:
            output = autocomplete.autocomplete(
                body["cell"],
                body["sources"],
                body["model_name"],
            )
        except exceptions.UnauthorizedException as e:
            raise tornado.web.HTTPError(
                HTTPStatus.UNAUTHORIZED.value, "Missing OpenAI API key"
            ) from e
        except exceptions.BadInputException as e:
            raise tornado.web.HTTPError(HTTPStatus.BAD_REQUEST.value, str(e)) from e

        logger.debug("Sending response: %s", output)
        self.finish(json.dumps({"data": output}))


def setup_handlers(web_app):
    host_pattern = ".*$"

    base_url = web_app.settings["base_url"]
    handlers = [(url_path_join(base_url, "jupyai", "autocomplete"), RouteHandler)]
    web_app.add_handlers(host_pattern, handlers)
