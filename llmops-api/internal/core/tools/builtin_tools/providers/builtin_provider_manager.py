"""
  @File    : builtin_provider_manager.py
  @Author  : Yue
  @Date    : 2026/5/8 19:26
  @Desc    : 
"""
import os.path
from typing import Any

import yaml
from injector import inject, singleton

from internal.core.tools.builtin_tools.entities import ProviderEntity, Provider


@inject
@singleton
class BuiltinProviderManager:
    """服务提供商工厂类"""
    provider_map: dict[str, Provider] = {}

    def __init__(self):
        self._get_provider_tool_map()

    def _get_provider_tool_map(self):
        """项目初始化的时候获取服务提供商、工具的夜摄关系并且填充provider_tool_map"""
        if self.provider_map:
            return
        current_path = os.path.abspath(__file__)
        providers_path = os.path.dirname(current_path)
        providers_yaml_path = os.path.join(providers_path, "providers.yaml")

        with open(providers_yaml_path, encoding="utf-8") as f:
            providers_yaml_data = yaml.safe_load(f)

        for idx, provider_data in enumerate(providers_yaml_data):
            provider_entity = ProviderEntity(**provider_data)
            self.provider_map[provider_entity.name] = Provider(
                name=provider_entity.name,
                position=idx + 1,
                provider_entity=provider_entity
            )

    def get_provider(self, provider_name: str) -> Provider:
        return self.provider_map.get(provider_name)

    def get_providers(self) -> list[Provider]:
        return list(self.provider_map.values())

    def get_provider_entities(self) -> list[ProviderEntity]:
        return [provider.provider_entity for provider in self.provider_map.values()]

    def get_tool(self, provider_name: str, tool_name: str) -> Any:
        provider = self.provider_map.get(provider_name)
        return provider.get_tool(tool_name) if provider else None
