# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
  @File    : http.py.py
  @Author  : Yue
  @Date    : 2026/3/24
  @Desc    :
"""
import logging
import traceback

from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate

from config import Config
from internal.exception import CustomException
from internal.extension import logging_extension, redis_extension, celery_extension
from internal.router import Router
from pkg.response import json, Response, HttpCode
from pkg.sqlalchemy import SQLAlchemy


class Http(Flask):
    def __init__(
            self,
            *args,
            conf: Config,
            db: SQLAlchemy,
            migrate: Migrate,
            router: Router,
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        CORS(self, resources={
            r"*": {
                "origins": "*",
                "supports_credentials": True,
                "methods": ["GET", "POST"],
                "allow_headers": ["content-type"],
            }
        })
        router.register_router(self)
        self.config.from_object(conf)
        # init database and bind to app
        db.init_app(self)
        migrate.init_app(self, db, "./internal/migration")
        redis_extension.init_app(self)
        logging_extension.init_app(self)
        celery_extension.init_app(self)

        # register exception handling
        self.register_error_handler(Exception, self._register_error_handler)

    def _register_error_handler(self, error: Exception):
        logging.error("An error occured: %s", error, exc_info=True)
        if isinstance(error, CustomException):
            return json(
                Response(
                    code=error.code,
                    message=error.message,
                    data=error.data if error.data else {},
                )
            )
        logging.error(traceback.format_exc())
        if self.debug:
            raise error
        return json(Response(
            code=HttpCode.FAIL,
            message=str(error),
            data={},
        ))
