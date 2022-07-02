from fastapi import FastAPI
import uvicorn

from app.common.config import conf

def create_app():
    """
    앱 실행 함수.
    :return:
    """
    # 설정
    app = FastAPI()
    # db initialize
    # redis initialize
    # middleware
    # router

    return app

app = create_app()

if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=conf().PROJ_RELOAD)
