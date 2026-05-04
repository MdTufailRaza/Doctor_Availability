"""Application-specific exceptions and handlers."""

from flask import jsonify


class APIError(Exception):
    """Raised when a request cannot be processed."""

    def __init__(self, message, status_code=400, payload=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}


def register_error_handlers(app):
    """Attach JSON error handlers to the application."""

    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = {"message": error.message, **error.payload}
        return jsonify(response), error.status_code

    @app.errorhandler(404)
    def handle_not_found(_error):
        return jsonify({"message": "Resource not found."}), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(_error):
        return jsonify({"message": "Method not allowed."}), 405

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception("Unhandled exception: %s", error)
        return jsonify({"message": "An unexpected server error occurred."}), 500
