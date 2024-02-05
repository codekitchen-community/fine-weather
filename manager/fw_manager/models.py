import json
from datetime import datetime, date
from typing import Optional, TYPE_CHECKING

import sqlalchemy.orm as so
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.model import Model

db = SQLAlchemy()

if TYPE_CHECKING:

    class BaseModel(Model, so.DeclarativeBase):
        """A dummy BaseModel class for type checking"""

        pass
else:
    BaseModel = db.Model


class CustomizedDumpsEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")
        return super().default(obj)


class Base(BaseModel):
    __abstract__ = True

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    created_at: so.Mapped[datetime] = so.mapped_column(default=func.now())
    updated_at: so.Mapped[datetime] = so.mapped_column(
        default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        attrs = {"id": self.id}
        if hasattr(self, "name"):
            attrs["name"] = self.name
        if hasattr(self, "title"):
            attrs["title"] = self.title
        return "<{} {}>".format(
            self.__class__.__name__, ",".join(f"{k}={v!r}" for k, v in attrs.items())
        )

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def as_json(self):
        return json.dumps(
            self.as_dict(), ensure_ascii=False, cls=CustomizedDumpsEncoder
        )


class User(Base):
    username: so.Mapped[str] = so.mapped_column(unique=True, index=True)
    password_hash: so.Mapped[str]


class Image(Base):
    uri: so.Mapped[str] = so.mapped_column(unique=True)
    thumbnail_uri: so.Mapped[str]
    title: so.Mapped[str]
    position: so.Mapped[Optional[str]]
    time: so.Mapped[Optional[str]]
    description: so.Mapped[Optional[str]]
    blurhash: so.Mapped[str]
    width: so.Mapped[int]
    height: so.Mapped[int]
