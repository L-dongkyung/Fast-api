from fastapi import FastAPI
from dataclasses import asdict
import uvicorn

from app.common.config import conf
from app.database.conn import db
from app.routes import index, auth

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
    # router
    app.include_router(index.router)
    app.include_router(auth.router, tags=['Authentication'])

    return app

app = create_app()

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=conf().PROJ_RELOAD)
