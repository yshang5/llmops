"""
  @File    : 
  @Author  : Yue
  @Date    : 2026/3/30
  @Desc    :
"""
from contextlib import contextmanager

from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy


class SQLAlchemy(_SQLAlchemy):
    """overwrite FLASK-sqlalchemy class to auto-commit"""

    @contextmanager
    def auto_commit(self):
        try:
            yield
            self.session.commit()
        except Exception as e:
            print("错误 ", e)
            self.session.rollback()
            raise e
