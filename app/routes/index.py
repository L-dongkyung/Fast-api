from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import Response

from app.database.conn import db
from app.database.schema import Users

router = APIRouter()

@router.get("/")
async def index(session: Session = Depends(db.session)):
    """
    ELB 상태 체크용 API
    :param session:
    :return:
    """

    "Users().create(session, auto_commit=True)"
    """
    user = Users(status = 'active')
    session.add(user)
    session.commit()
    """

    current_time = datetime.utcnow()
    return Response(f"Fast-api check API (UTC: {current_time.strftime('%Y.%m.%d %H:%M:%S')})")

@router.get("/test")
async def test(request: Request):
    current_time = datetime.utcnow()
    return Response(f"test api Done (UTC: {current_time.strftime('%Y-%m-%d %H:%M:%S')})")
