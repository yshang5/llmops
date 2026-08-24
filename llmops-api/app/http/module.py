# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
  @File    : module.py
  @Author  : Yue
  @Date    : 2026/3/30
  @Desc    :
"""
from flask_migrate import Migrate
from injector import Module, Binder, Injector

from internal.extension.database_extension import db
from internal.extension.migrate_extension import migrate
from internal.extension.redis_extension import redis_client
from pkg.sqlalchemy import SQLAlchemy
from redis import Redis


class ExtensionModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(SQLAlchemy, to=db)
        binder.bind(Migrate, to=migrate)
        binder.bind(Redis, to=redis_client)


injector = Injector([ExtensionModule])
