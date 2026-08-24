# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
  @File    : test_app_handler.py
  @Author  : Yue
  @Date    : 2026/3/30
  @Desc    :
"""
import pytest

from pkg.response import HttpCode


class TestAppHandler:

    @pytest.mark.parametrize(
        "app_id, query",
        [
            ("0f67cfc5-6b93-4ae4-9402-34b137a21628", "你好，你是"),
            ("0f67cfc5-6b93-4ae4-9402-34b137a21628", None),
        ]
    )
    def test_completion(self, app_id, query, client):
        resp = client.post(f"/apps/{app_id}/debug", json={"query": query})
        assert resp.status_code == 200
        if not query:
            assert resp.json.get("code") == HttpCode.VALIDATE_ERROR
        else:
            assert resp.json.get("code") == HttpCode.SUCCESS
