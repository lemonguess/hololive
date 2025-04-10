from fastapi.responses import JSONResponse
from starlette import status


class ResponseUtil:
    @staticmethod
    def success(data=None, message="success", status_code=status.HTTP_200_OK):
        return JSONResponse(status_code=status_code,
                            content={"code": 0, "msg": message, "data": data})

    @staticmethod
    def error(message="error", status_code=status.HTTP_400_BAD_REQUEST, code=1):
        return JSONResponse(status_code=status_code,
                            content={"code": code, "msg": message, "data": ""})
