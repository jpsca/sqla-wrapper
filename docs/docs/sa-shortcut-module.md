# `sa` shortcut module

This library includes a `sa` module from which you can import any of the functions or classes from `sqlalchemy` and `sqlalchemy.orm`. It is an optional helper if you prefer not having a "star import" (`from sqlalchemy import *`) in your code.

Instead of doing:

```python
from sqlalchemy import Column, DateTime, ForeignKey, String, select
# from sqlalchemy import *  # noqa
from sqlalchemy.orm import relationship
from app.models import Base, dbs


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    user_id = Column(ForeignKey("users.id"))
    user = relationship("User", back_populates="tags")

    @classmethod
    def get_all(cls):
        return dbs.execute(
            select(cls).order_by(cls.published_at.desc())
        ).scalars().all()
```

You can use:

```python
from app.models import Base, dbs, sa

class Tag(Base):
    __tablename__ = "tags"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    created_at = sa.Column(sa.DateTime, nullable=False)
    user_id = sa.Column(sa.ForeignKey("users.id"))
    user = sa.relationship("User", back_populates="tags")

    @classmethod
    def get_all(cls):
        return dbs.execute(
            sa.select(cls).order_by(cls.published_at.desc())
        ).scalars().all()
```
