from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    error_dict = {}
    for error in exc.errors():
        field = error["loc"][-1]
        message = error["msg"]
        error_dict[field] = message

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"errors": error_dict},
    )
