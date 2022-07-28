import time, re
import jwt

import sqlalchemy.exc

from jwt.exceptions import ExpiredSignatureError, DecodeError
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.common import consts
from app.utils.date_utils import Date
from app.utils.logger import api_logger
from app.common.consts import EXCEPT_PATH_LIST, EXCEPT_PATH_REGEX
from app.models import UserToken
from app.error import exception as ex
from app.error.exception import APIException, SqlFailureEx, APIQueryStringEX

async def access_control(request: Request, call_next):
    request.state.req_time = Date.datetime()
    request.state.start = time.time()
    request.state.inspect = None
    request.state.user = None
    request.state.service = None

    ip = request.headers['x-forwarded-for'] if 'x-forwarded-for' in request.headers.keys() else request.client.host
    request.state.ip = ip.split(',')[0] if ',' in ip else ip
    headers = request.headers
    cookies = request.cookies

    url = request.url.path
    if await url_pattern_check(url, EXCEPT_PATH_REGEX) or url in EXCEPT_PATH_LIST:
        response = await call_next(request)
        # if url != '/':
            # await api_logger(request=request, response=response)
        return response
    try:
        if url.startswith('/api'):
            # api token 검사
            if "Authorization" in headers.keys():
                token_info = await token_decode(access_token=headers.get("Authorization"))
                request.state.user = UserToken(**token_info)
            else:
                if "Authorization" not in headers.keys():
                    raise ex.NotAuthorized()
        else:
            # 템플릿 렌더링?인 경우 쿠키로 검사.
            cookies['Authorization'] = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MTAsImVtYWlsIjoidXNlckBleGFtcGxlLmNvbSIsIm5hbWUiOm51bGwsInBob25lX251bWJlciI6bnVsbH0.tJUIk7nWYIcUL5oWWPWbd-SHy4X9u6NWNxcneYLe1aE"
            if "Authorization" not in request.cookies.keys():
                raise ex.NotAuthorized()
            user_info = await token_decode(access_token=request.cookies.get("Authorization"))
            request.state.user = UserToken(**user_info)

        response = await call_next(request)
        await api_logger(request=request, response=response)
    except Exception as e:
        error = await exception_handler(e)
        error_dict = dict(status_code=error.status_code, msg=error.msg, detail=error.detail, code=error.code)
        response = JSONResponse(status_code=error.status_code, content=error_dict)
        await api_logger(request=request, error=error)
    return response


async def url_pattern_check(path, pattern):
    result = re.match(pattern, path)
    if result:
        return True
    return False

async def token_decode(access_token):
    """
    :param access_token:
    :return:
    """
    try:
        access_token = access_token.replace("Bearer ", "")
        payload = jwt.decode(access_token, key=consts.JWT_SECRET, algorithms=[consts.JWT_ALGORITHM])
    except ExpiredSignatureError:
        raise ex.TokenExpiredEx()
    except DecodeError:
        raise ex.TokenDecodeEx()
    return payload

async def exception_handler(error: Exception):
    print(error)
    if isinstance(error, sqlalchemy.exc.OperationalError):
        error = SqlFailureEx(ex=error)
    if not isinstance(error, APIException):
        error = APIException(ex=error, detail=str(error))
    return error
