from datetime import datetime, timedelta

from sqlalchemy import Column, Integer, String, DateTime, func, Enum, Boolean
from sqlalchemy.orm import Session
from app.database.conn import Base

class BaseMixin:
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, nullable=False, default=func.utc_timestamp())
    updated_at = Column(DateTime, nullable=False, default=func.utc_timestamp(), onupdate=func.utc_timestamp())

    def all_colums(self):
        return [c for c in self.__table__.colums if c.primary_key is False and c.name != "created_at"]

    def __hash__(self):
        return hash(self.id)

    def create(self, session: Session, auto_commit: bool = False, **kwargs):
        """

        :param session:
        :param auto_commit:
        :param kwargs:
        :return:
        """
        for col in self.all_colums():
            col_name = col.name
            if col_name in kwargs:
                setattr(self, col_name, kwargs.get(col_name))
        session.add(self)
        session.flush()
        if auto_commit:
            session.commit()
        return self


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