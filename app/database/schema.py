from datetime import datetime, timedelta

from sqlalchemy import Column, Integer, String, DateTime, func, Enum, Boolean
from sqlalchemy.orm import Session
from app.database.conn import Base, db

class BaseMixin:
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, nullable=False, default=func.utc_timestamp())
    updated_at = Column(DateTime, nullable=False, default=func.utc_timestamp(), onupdate=func.utc_timestamp())

    def all_colums(self):
        return [c for c in self.__table__.columns if c.primary_key is False and c.name != "created_at"]

    def __hash__(self):
        return hash(self.id)

    @classmethod
    def create(cls, session: Session, auto_commit: bool = False, **kwargs):
        """

        :param session:
        :param auto_commit:
        :param kwargs:
        :return:
        """
        obj = cls()
        for col in obj.all_colums():
            col_name = col.name
            if col_name in kwargs:
                setattr(obj, col_name, kwargs.get(col_name))
        session.add(obj)
        session.flush()
        if auto_commit:
            session.commit()
        return obj

    @classmethod
    def get(cls, **kwargs):
        """
        DB에서 정보(row)를 가져오는 함수.
        :param kwargs:
        :return:
        """
        session = next(db.session())
        query = session.query(cls)
        for key, value in kwargs.items():
            col = getattr(cls, key)
            query = query.filter(col == value)

        if query.count() > 1:
            raise Exception("하나의 데이터 리턴만 지원. 결과가 하나 이상입니다.")
        return query.first()


class Users(Base, BaseMixin):
    __tablename__ = "users"
    status = Column(Enum("active", "deleted", "blocked"), default="active")
    email = Column(String(length=255), nullable=True)
    pw = Column(String(length=2000), nullable=True)
    name = Column(String(length=255), nullable=True)
    phone_number = Column(String(length=20), nullable=True, unique=True)
    profile_img = Column(String(length=1000), nullable=True)
    sns_type = Column(Enum("FB", "G", "K"), nullable=True)
    marketing_agree = Column(Boolean, nullable=True, default=False)