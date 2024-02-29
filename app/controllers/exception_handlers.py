from fastapi import FastAPI, status, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import (
    RequestValidationError,
    ResponseValidationError,
    ValidationException,
)
from fastapi.responses import JSONResponse
from fastapi_another_jwt_auth.exceptions import AuthJWTException
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.controllers.exceptions import NotFoundException
from app.logger import logger
import traceback

log = logger.extendable_logger(log_name="Exception Handler")


def register_exception_handler(app: FastAPI):
    @app.exception_handler(NotFoundException)
    async def http_exception_handler(request, exc) -> JSONResponse:
        """
        Not Found Exception Handler

        :param request: ``Request``: The request object
        :param exc: ``NotFoundException``: The exception object

        :return: ``JSONResponse``: The JSON response
        """
        return JSONResponse(
            content=jsonable_encoder({"detail": exc.detail}),
            status_code=status.HTTP_404_NOT_FOUND,
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request, exc) -> JSONResponse:
        """
        SQLAlchemy Exception Handler

        :param request: ``Request``: The request object
        :param exc: ``SQLAlchemyError``: The exception object

        :return: ``JSONResponse``: The JSON response
        """

        log.error(f"SQLAlchemyError: {exc}", exc_info=1)
        log.error(traceback.format_exc())

        # Handle SQLAlchemy errors here
        # You can perform logging, custom error responses, etc.
        return JSONResponse(
            content=jsonable_encoder({"detail": "DB Service Unavailable"}),
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    @app.exception_handler(ValidationError)
    @app.exception_handler(ValidationException)
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc) -> JSONResponse:
        errors = exc.errors()
        formatted_errors = []
        flag = True

        for error in errors:
            if flag:
                field = error.get("loc", None) or error.get("input", None)
                msg = error.get("msg", "Validation error")
                err_type = error.get("type", None)
                field_len = len(field) if hasattr(field, "__len__") else 0

                if err_type == "json_invalid":
                    msg = "JSON parse error"
                    field_val = "Request body"
                elif err_type == "model_attributes_type" and field[0] == "body":
                    field_val = "Request body"
                elif err_type == "model_attributes_type":
                    field_val = "Response body"
                elif field_len > 2 and (
                    (hasattr(field[1], "startswith") and field[1].startswith("list"))
                    or (hasattr(field[2], "startswith") and field[2].startswith("list"))
                ):
                    field_val = field[1]
                    flag = False
                else:
                    field_val = "None"
                    if field_len == 1:
                        field_val = field
                    elif field_len > 1:
                        field_val = field[-1]

                if field:
                    formatted_errors.append(
                        {
                            "field": field_val,
                            "error_description": msg,
                        }
                    )
            else:
                flag = True

        return JSONResponse(
            content=jsonable_encoder(
                {
                    "detail": {"errors": formatted_errors},
                    # "other": {"msg": msg, "data": data},
                }
            ),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    @app.exception_handler(ResponseValidationError)
    async def response_validation_exception_handler(request, exc) -> JSONResponse:
        """
        Response Validation Exception Handler

        :param request: ``Request``: The request object
        :param exc: ``ResponseValidationError``: The exception object

        :return: ``JSONResponse``: The JSON response
        """
        log.error(f"ResponseValidationError: {exc}", exc_info=1)
        log.error(traceback.format_exc())

        # Handle Response Validation errors here
        # You can perform logging, custom error responses, etc.
        return JSONResponse(
            content=jsonable_encoder({"detail": "Response Validation Failed"}),
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    @app.exception_handler(AuthJWTException)
    async def token_header_exception_handler(request, exc) -> JSONResponse:
        """
        JWT Token Header Exception Handler

        :param request: ``Request``: The request object
        :param exc: ``AuthJWTException``: The exception object

        :return: ``JSONResponse``: The JSON response
        """
        log.error(f"JWT Token: {exc}", exc_info=1)
        log.error(traceback.format_exc())

        # Handle JWT errors here
        # You can perform logging, custom error responses, etc.
        return JSONResponse(
            content=jsonable_encoder({"detail": "Bad Token Header"}),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    @app.exception_handler(Exception)
    async def all_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """
        Global exception handler and logger

        :param request: ``Request``: The request object
        :param exc: ``Exception``: The exception object

        :return: ``JSONResponse``: The JSON response
        """
        log.error(f"Global Exception: {exc}", exc_info=1)
        log.error(traceback.format_exc())

        # Handle errors not caught by other exception handlers
        # You can perform logging, custom error responses, etc.
        return JSONResponse(
            content=jsonable_encoder({"detail": "Internal Server Error"}),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
