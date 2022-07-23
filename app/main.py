from fastapi import FastAPI
from dataclasses import asdict
import uvicorn

from app.common.config import conf
from app.common.consts import EXCEPT_PATH_LIST, EXCEPT_PATH_REGEX
from app.database.conn import db

from app.middlewares.trusted_hosts import TrustedHostMiddleware
from app.middlewares.token_validator import AccessControl
from app.routes import index, auth, users
from starlette.middleware.cors import CORSMiddleware

def create_app():
    """
    앱 실행 함수.
    :return:
    """
    # 설정
    c = conf()
    app = FastAPI()
    conf_dict = asdict(c)
    db.init_app(app, **conf_dict)
    # Base.metadata.create_all(db.engine)

    # db initialize
    # redis initialize
    # middleware
    app.add_middleware(AccessControl, except_path_list=EXCEPT_PATH_LIST, except_path_regex=EXCEPT_PATH_REGEX)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=conf().ALLOW_SITE,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*']
    )
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=conf().TRUSTED_HOSTS, except_path=['/health'])

    # router
    app.include_router(index.router)
    app.include_router(auth.router, tags=['Authentication'])
    app.include_router(users.router, prefix="/api")

    return app

app = create_app()

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=conf().PROJ_RELOAD)
