# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
  @File    : exception.py
  @Author  : Yue
  @Date    : 2026/3/30
  @Desc    :
"""
from dataclasses import field
from typing import Any

from pkg.response import HttpCode


class CustomException(Exception):
    code: HttpCode = HttpCode.FAIL
    message: str = ""
    data: Any = field(default_factory=dict)

    def __init__(self, message: str = "", data: Any = None):
        super().__init__()
        self.message = message
        self.data = data


class FailException(CustomException):
    pass


class NotFoundException(CustomException):
    code = HttpCode.NOT_FOUND


class UnauthorizedException(CustomException):
    code = HttpCode.UNAUTHORIZED


class ForbiddenException(CustomException):
    code = HttpCode.FORBIDDEN


class ValidateErrorException(CustomException):
    code = HttpCode.VALIDATE_ERROR
