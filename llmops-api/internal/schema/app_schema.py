# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
  @File    : app_schema.py
  @Author  : Yue
  @Date    : 2026/3/29
  @Desc    :
"""
from flask_wtf import FlaskForm
from wtforms.fields.simple import StringField
from wtforms.validators import DataRequired, Length


class CompletionReq(FlaskForm):
    query = StringField("query", validators=[
        DataRequired(message="query is required"),
        Length(max=2000, message="maximum length is 2000")
    ])
