import re
import time
import typing
import jwt

from fastapi.params import Header
from jwt import PyJWTError
from pydantic import BaseModel
from starlette.requests import Request
from starlette.datastructures import URL, Headers
from starlette.responses import JSONResponse, PlainTextResponse, RedirectResponse, Response
from starlette.types import ASGIApp, Receive, Send, Scope

from app.common import config, consts
from app.common.config import conf
from app.models import UserToken

from app.utils.date_utils import Date


class AccessControl:
    def __init__(
            self,
            app: ASGIApp,
            except_path_list: typing.Sequence[str] = None,
            except_path_regex: str = None
    ) -> None:
        if except_path_list is None:
            except_path_list = ['*']
        self.app = app
        self.except_path_list = except_path_list
        self.except_path_regex = except_path_regex

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        미들웨어 토큰을 검증하는 곳
        :param scope:
        :param receive:
        :param send:
        :return:
        """
        print(self.except_path_regex)
        print(self.except_path_list)

        request = Request(scope=scope)
        headers = Headers(scope=scope)

        request.state.req_time = Date.datetime()
        print(Date.datetime())
        print(Date.date())
        print(Date.date_num())
        request.state.start = time.time()
        request.state.inspect = None
        request.state.user = None
        request.state.is_admin_access = None
        ip_from = request.headers['x-forwarded-for'] if "x-forwarded-for" in request.headers.keys() else None  # AWS ELB 통과 후 설정.

        if await self.url_pattern_check(request.url.path, self.except_path_regex) or request.url.path in self.except_path_list:
            return await self.app(scope, receive, send)

        if request.url.path.startswith("/api"):
            if "Authorization" in request.headers.keys():
                request.state.user = await self.token_decode(access_token=request.headers.get("Authorization"))
            else:
                response = JSONResponse(status_code=401, content=dict(msg="AUTHORIZATION_REQUIRED"))
                return await response(scope, receive, send)
        else:
            # 쿠키의 토큰을 받으려면 현 if구절을 주석하여 login 후 토큰을 이곳에 입력해야함.
            request.cookies['Authorization'] = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MTAsImVtYWlsIjoidXNlckBleGFtcGxlLmNvbSIsIm5hbWUiOm51bGwsInBob25lX251bWJlciI6bnVsbH0.tJUIk7nWYIcUL5oWWPWbd-SHy4X9u6NWNxcneYLe1aE"
            if "Authorization" not in request.cookies.keys():
                response = JSONResponse(status_code=401, content=dict(msg="AUTHORIZATION_REQUIRED"))
                return await response(scope, receive, send)
            request.state.user = await self.token_decode(access_token=request.cookies.get("Authorization"))

        request.state.req_time = Date.datetime()
        return await self.app(scope, receive, send)

    @staticmethod
    async def url_pattern_check(path, pattern):
        res = re.match(pattern, path)
        if res:
            return True
        return False

    @staticmethod
    async def token_decode(access_token):
        try:
            access_token = access_token.replace("Bearer ", "")
            payload = jwt.decode(access_token, key=consts.JWT_SECRET, algorithms=[consts.JWT_ALGORITHM])
        except PyJWTError as e:
            print(e)
            raise
            # 에러 발생 코드 추가 예정
        return payload
