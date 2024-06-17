import json

from flask_restx import Api
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException


def handle_validation_error(e: ValidationError) -> tuple[dict, int]:
    return {"error": "validation_error", "message": json.loads(e.json(include_url=False, include_context=False))}, 400


def handle_value_error(e: ValueError) -> tuple[dict, int]:
    return {"error": "value_error", "message": str(e)}, 400


def handle_http_exception(e: HTTPException) -> tuple[dict, int]:
    return {"error": "http_exception", "message": e.description or e.name}, e.code or 500


def handle_internal_error(e: Exception) -> tuple[dict, int]:
    return {"error": "internal_server_error", "message": str(e)}, 500


def init_error_handlers(api: Api) -> None:
    api.error_handlers[ValidationError] = handle_validation_error  # type: ignore
    api.error_handlers[ValueError] = handle_value_error  # type: ignore
    api.error_handlers[HTTPException] = handle_http_exception  # type: ignore
    api.error_handlers[Exception] = handle_internal_error  # type: ignore
