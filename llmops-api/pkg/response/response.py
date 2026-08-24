# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
  @File    : response.py
  @Author  : Yue
  @Date    : 2026/3/29
  @Desc    :
"""
from dataclasses import field, dataclass
from typing import Any

from flask import jsonify

from pkg.response.http_code import HttpCode


@dataclass
class Response:
    code: HttpCode = HttpCode.SUCCESS
    message: str = ""
    data: Any = field(default_factory=dict)


def json(data: Response = None):
    return jsonify(data), 200


def success_json(data: Any = None):
    return json(Response(code=HttpCode.SUCCESS, data=data))


def fail_json(data: Any = None):
    return json(Response(code=HttpCode.FAIL, data=data))


def validate_error_json(errors: dict = None):
    first_key = next(iter(errors))
    msg = ""
    if first_key:
        msg = errors.get(first_key)[0]
    return json(Response(code=HttpCode.VALIDATE_ERROR, data=errors, message=msg))


def message(code: HttpCode, msg: str = ""):
    return json(Response(code=code, message=msg, data={}))


def success_message(msg: str = ""):
    return message(code=HttpCode.SUCCESS, msg=msg)


def fail_message(msg: str = ""):
    return message(code=HttpCode.FAIL, msg=msg)


def not_found_message(msg: str = ""):
    return message(code=HttpCode.NOT_FOUND, msg=msg)


def unauthorized(msg: str = ""):
    return message(code=HttpCode.UNAUTHORIZED, msg=msg)


def forbidden(msg: str = ""):
    return message(code=HttpCode.FORBIDDEN, msg=msg)
