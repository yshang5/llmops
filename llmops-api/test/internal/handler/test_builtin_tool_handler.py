"""
  @File    : test_builtin_tool_handler.py
  @Author  : Yue
  @Date    : 2026/5/18 12:39
  @Desc    : 
"""
import pytest
from pkg.response import HttpCode


class TestBuiltinToolHandler:
    """内置工具处理器测试类"""

    def test_get_categories(self, client):
        """测试获取所有分类信息"""
        resp = client.get("/builtin-tools/categories")
        assert resp.status_code == 200
        assert resp.json.get("code") == HttpCode.SUCCESS
        assert len(resp.json.get("data")) > 0

    def test_get_builtin_tools(self, client):
        resp = client.get("/builtin-tools")
        assert resp.status_code == 200
        assert resp.json.get("code") == HttpCode.SUCCESS
        assert len(resp.json.get("data")) > 0

    @pytest.mark.parametrize("provider_name, tool_name", [
        ("google", "google_serper"),
        ("imooc", "imooc_llomps"),
    ])
    def test_get_provider_tools(self, provider_name, tool_name, client):
        resp = client.get(f"/builtin-tools/{provider_name}/tools/{tool_name}")
        assert resp.status_code == 200
        if provider_name == "google":
            assert resp.json.get("code") == HttpCode.SUCCESS
            assert len(resp.json.get("data")) > 0
        elif provider_name == "imooc":
            assert resp.json.get("code") == HttpCode.NOT_FOUND

    @pytest.mark.parametrize("provider_name", [
        "google",
        "imooc",
    ])
    def test_get_provider_icon(self, provider_name, client):
        resp = client.get(f"/builtin-tools/{provider_name}/icon")
        assert resp.status_code == 200
        if provider_name == "imooc":
            assert resp.json.get("code") == HttpCode.NOT_FOUND
