"""
  @File    : 
  @Author  : Yue
  @Date    : 2026/3/30
  @Desc    :
"""
import uuid
from dataclasses import dataclass

from injector import inject

from internal.model.app import App
from pkg.sqlalchemy import SQLAlchemy


@inject
@dataclass
class AppService:
    """app service logic"""
    db: SQLAlchemy

    def create_app(self) -> App:
        with self.db.auto_commit():
            # 1. construct model object
            app = App(name="测试机器人", account_id=uuid.uuid4(), icon="", description="聊天机器人", )
            # 2. add
            self.db.session.add(app)
        return app

    def get_app(self, id: uuid.UUID) -> App:
        return self.db.session.query(App).get(id)

    def update_app(self, id: uuid.UUID) -> App:
        with self.db.auto_commit():
            app = self.get_app(id)
            app.name = "updated name"
        return app

    def delete_app(self, id: uuid.UUID) -> App:
        with self.db.auto_commit():
            app = self.get_app(id)
            self.db.session.delete(app)
        return app
