"""
  @File    : api_provider_manager.py
  @Author  : Yue
  @Date    : 2026/6/1 16:10
  @Desc    : 
"""
import requests
from injector import inject
from dataclasses import dataclass
from typing import Type, Optional, Callable
from langchain_core.tools import BaseTool, StructuredTool
from pydantic import BaseModel, create_model, Field
from internal.core.tools.api_tools.entities import ToolEntity, ParameterTypeMap, ParameterIn


@inject
@dataclass
class ApiProviderManager(BaseModel):
    """API工具提供者管理器，能根据传递的工具配置信息生成自定义的LangChain工具"""

    @classmethod
    def _create_model_from_parameters(cls, parameters: list[dict]) -> Type[BaseModel]:
        fields = {}
        for parameter in parameters:
            field_name = parameter.get("name")
            field_type = ParameterTypeMap.get(parameter.get("type"), str)
            field_required = parameter.get("required", True)
            field_description = parameter.get("description", "")

            fields[field_name] = (
                field_type if field_required else Optional[field_type],
                Field(description=field_description),
            )

        return create_model("DynamicModel", **fields)

    @classmethod
    def _create_tool_func_from_tool_entity(cls, tool_entity: ToolEntity) -> Callable:
        def tool_func(**kwargs) -> str:
            """Api工具请求参数"""
            # 1. 定义变量存储来自于path/query/header/cookie/request_body中的数据
            param_buckets = {
                ParameterIn.PATH: {},
                ParameterIn.HEADER: {},
                ParameterIn.QUERY: {},
                ParameterIn.COOKIE: {},
                ParameterIn.REQUEST_BODY: {},
            }
            parameter_map = {
                parameter.get("name"): parameter for parameter in tool_entity.parameters
            }

            header_map = {
                header.get("key"): header for header in tool_entity.headers
            }

            for key, value in kwargs.items():
                parameter = parameter_map.get(key)
                if parameter is None:
                    continue
                param_buckets[parameter.get("in", ParameterIn.QUERY)][key] = value

            return requests.request(
                method=tool_entity.method,
                url=tool_entity.url.format(**param_buckets[ParameterIn.PATH]),
                params=param_buckets[ParameterIn.QUERY],
                json=param_buckets[ParameterIn.REQUEST_BODY],
                headers={**header_map, **param_buckets[ParameterIn.HEADER]},
                cookies=param_buckets[ParameterIn.COOKIE],
            ).text

        return tool_func

    def get_tool(self, tool_entity: ToolEntity) -> BaseTool:
        """根据传递的配置获取自定义API工具"""
        return StructuredTool.from_function(
            func=self._create_tool_func_from_tool_entity(tool_entity),
            name=f"{tool_entity.id}_{tool_entity.name}",
            description=tool_entity.description,
            args_schema=self._create_model_from_parameters(parameters=tool_entity.parameters),
        )
