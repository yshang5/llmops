"""
  @File    : builtin_tool_service.py
  @Author  : Yue
  @Date    : 2026/5/10 19:12
  @Desc    : 
"""
import mimetypes
import os.path
from dataclasses import dataclass

from flask import current_app
from injector import inject
from pydantic import BaseModel

from internal.core.tools.builtin_tools.categories import BuiltinCategoryManager
from internal.core.tools.builtin_tools.providers import BuiltinProviderManager
from internal.exception import NotFoundException
from typing import Any


@inject
@dataclass
class BuiltinToolService:
    """内置工具服务"""
    builtin_tool_manager: BuiltinProviderManager
    build_category_manager: BuiltinCategoryManager

    def get_builtin_tools(self) -> list:
        """获取LLMOps项目中的所有内置工具信息 + 提供商信息"""
        providers = self.builtin_tool_manager.get_providers()
        builtin_tools = []
        for provider in providers:
            provider_entity = provider.provider_entity
            builtin_tool = {
                **provider_entity.model_dump(exclude={"icon"}),
                "tools": [],
            }
            for tool_entity in provider.get_tool_entities():
                tool = provider.get_tool(tool_entity.name)
                tool_dict = {
                    **tool_entity.model_dump(exclude={"icon"}),
                    "inputs": self.get_tool_inputs(tool)
                }
                builtin_tool["tools"].append(tool_dict)
            builtin_tools.append(builtin_tool)
        return builtin_tools

    def get_provider_tool(self, provider_name: str, tool_name: str):
        provider = self.builtin_tool_manager.get_provider(provider_name)
        if provider is None:
            raise NotFoundException(f"该提供商{provider_name}不存在")
        tool_entity = provider.get_tool_entity(tool_name)
        if tool_entity is None:
            raise NotFoundException(f"该工具{tool_name}不存在")
        provider_entity = provider.provider_entity
        tool = provider.get_tool(tool_name)
        builtin_tool = {
            "provider": {**provider_entity.model_dump(exclude={"icon", "created_at"})},
            **tool_entity.model_dump(),
            "created_at": provider_entity.created_at,
            "inputs": self.get_tool_inputs(tool)
        }
        return builtin_tool

    @classmethod
    def get_tool_inputs(cls, tool) -> list:
        inputs = []
        if hasattr(tool, "args_schema") and issubclass(tool.args_schema, BaseModel):
            for field_name, model_field in tool.args_schema.model_fields.items():
                inputs.append({
                    "name": field_name,
                    "description": model_field.description or "",
                    "required": model_field.is_required(),
                    "type": getattr(model_field.annotation, "__name__", str(model_field.annotation)),
                })
        return inputs

    def get_provider_icon(self, provider_name: str) -> tuple[bytes, str]:
        """根据传递的供应商名字获取icon图标流信息"""
        # 1. 获取对用的工具供应商
        provider = self.builtin_tool_manager.get_provider(provider_name)
        if not provider:
            raise NotFoundException(f"该工具提供者{provider_name}不存在")
        # 2. 获取项目的根路径信息
        root_path = os.path.dirname(os.path.dirname(current_app.root_path))

        # 3. 拼接icon资源文件夹
        provider_path = os.path.join(root_path, "internal", "core", "tools", "builtin_tools", "providers",
                                     provider_name)

        icon_path = os.path.join(provider_path, "_asset", provider.provider_entity.icon)
        if not os.path.exists(icon_path):
            raise NotFoundException(f"该工具提供者未找到图标")
        mimetype, _ = mimetypes.guess_type(icon_path)
        mimetype = mimetype or "application/octet-stream"
        with open(icon_path, "rb") as f:
            byte_data = f.read()
            return byte_data, mimetype

    def get_categories(self) -> list[dict[str, Any]]:
        """获取所有内置提供商的分类信息, 涵盖了category,name,icon"""
        category_map = self.build_category_manager.get_category_map()
        return [
            {
                "name": category["entities"].name,
                "category": category["entities"].category,
                "icon": category["icon"]
            }
            for category in category_map.values()
        ]
