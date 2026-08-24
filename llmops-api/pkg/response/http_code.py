# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
  @File    : http_code.py
  @Author  : Yue
  @Date    : 2026/3/29
  @Desc    :
"""
from enum import Enum


class HttpCode(str, Enum):
    SUCCESS = "success"
    FAIL = "fail"
    NOT_FOUND = "not found"
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    VALIDATE_ERROR = "validate_error"
