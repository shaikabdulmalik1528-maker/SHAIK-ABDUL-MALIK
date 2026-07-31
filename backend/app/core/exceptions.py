from fastapi import Request, status
from fastapi.responses import JSONResponse
import time

class AssessmentPlatformException(Exception):
    def __init__(self, message: str, status_code: int = 400, error_code: str = "BAD_REQUEST"):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)

class DuplicateAssessmentError(AssessmentPlatformException):
    def __init__(self, message: str = "Duplicate gesture attempt detected. Request rejected."):
        super().__init__(message=message, status_code=status.HTTP_409_CONFLICT, error_code="DUPLICATE_ENTRY")

class LandmarkValidationError(AssessmentPlatformException):
    def __init__(self, message: str = "Hand landmarks incomplete or malformed."):
        super().__init__(message=message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, error_code="INVALID_LANDMARKS")

def register_exception_handlers(app):
    @app.exception_handler(AssessmentPlatformException)
    async def custom_exception_handler(request: Request, exc: AssessmentPlatformException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.error_code,
                    "message": exc.message
                },
                "timestamp": time.time()
            }
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        # Print actual error trace in terminal for debugging
        print(f"[CRITICAL UNHANDLED ERROR]: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": str(exc)
                },
                "timestamp": time.time()
            }
        )