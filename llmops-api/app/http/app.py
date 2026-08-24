# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
  @File    : app.py.py
  @Author  : Yue
  @Date    : 2026/3/24
  @Desc    :
"""
import dotenv
from flask_migrate import Migrate

from config import Config
from internal.router import Router
from internal.server.http import Http
from pkg.sqlalchemy import SQLAlchemy
from .module import injector

# load config from .env file
dotenv.load_dotenv()

config = Config()

# init flask app
app = Http(
    __name__,
    conf=config,
    db=injector.get(SQLAlchemy),
    migrate=injector.get(Migrate),
    router=injector.get(Router)
)

celery = app.extensions["celery"]

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
