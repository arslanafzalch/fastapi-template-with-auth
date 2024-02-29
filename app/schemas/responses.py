from typing import List

from pydantic import BaseModel, Field


class CustomValidationResponse(BaseModel):
    field: str
    error_description: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "field": "email",
                    "error_description": "Input should be a valid string",
                }
            ]
        }
    }


class CustomValidationsResponse(BaseModel):
    detail: List[CustomValidationResponse]


class CustomInternalServerResponse(BaseModel):
    detail: str = "Internal Server Error"


class CustomJSONResponse(BaseModel):
    detail: str = Field(
        description="Message from the server",
        example="Operation Successful",
    )


class CustomAlreadyReportedResponse(BaseModel):
    detail: str = Field(
        description="Message from the server",
        example="Already accessed",
    )


class CustomServiceUnavailableResponse(BaseModel):
    detail: str = Field(
        description="Message from the server",
        example="Already accessed",
    )


class CustomUnAuthorizedResponse(BaseModel):
    detail: str = Field(
        description="Message from the server",
        example="Invalid Token",
    )


def common_responses(response_model=CustomJSONResponse, include_model=True):
    data = {
        "response_model": response_model,
        "responses": {
            401: {
                "model": CustomUnAuthorizedResponse,
                "description": "Unauthorized",
            },
            422: {"model": CustomValidationsResponse, "exclude_defaults": True},
            500: {
                "model": CustomInternalServerResponse,
            },
        },
    }

    if not include_model:
        data.pop("response_model", None)

    return data
