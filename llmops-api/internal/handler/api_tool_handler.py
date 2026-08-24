"""
  @File    : api_tool_handler.py
  @Author  : Yue
  @Date    : 2026/5/21 03:55
  @Desc    : 
"""
from injector import inject
from dataclasses import dataclass
from internal.schema.api_tool_schema import (
    ValidateOpenAPISchemaReq,
    CreateApiToolReq,
    GetApiToolProviderResp,
    GetApiToolResp,
    GetApiToolProvidersWithPageReq,
    GetApiToolProvidersWithPageResp,
    UpdateApiToolProviderReq,
)
from internal.service import ApiToolService
from pkg.response import validate_error_json, success_message, success_json
from pkg.paginator import PageModel
import uuid
from flask import request


@inject
@dataclass
class ApiToolHandler:
    """自定义API插件处理器"""
    api_tool_service: ApiToolService

    def create_api_tool_provider(self):
        """创建自定义api工具"""
        # 1 提取请求并校验
        req = CreateApiToolReq()
        if not req.validate():
            return validate_error_json(req.errors)
        # 2 调用服务创建api工具
        self.api_tool_service.create_api_tool(req)
        return success_message("创建自定义API插件成功")

    def get_api_tool(self, provider_id: uuid.UUID, tool_name: str):
        """根据provider_id + tool_name获取工具的详情信息"""
        api_tool = self.api_tool_service.get_api_tool(provider_id, tool_name)
        resp = GetApiToolResp()
        return success_json(resp.dump(api_tool))

    def validate_openapi_schema(self):
        """校验传递的openapi_schema字段是否正确"""
        # 1. 校验前端的数据
        req = ValidateOpenAPISchemaReq()
        if not req.validate():
            return validate_error_json(req.errors)
        # 2.调用服务并解析传递数据
        self.api_tool_service.parse_openapi_schema(req.openapi_schema.data)
        return success_message("数据校验成功")

    def get_api_tool_provider(self, provider_id: uuid.UUID):
        """根据传递的provider_id 获取工具提供这的原始信息"""
        api_tool_provider = self.api_tool_service.get_api_tool_provider(provider_id)
        resp = GetApiToolProviderResp()
        return success_json(resp.dump(api_tool_provider))

    def delete_api_tool_provider(self, provider_id: uuid.UUID):
        """根据传递的provider_id 删除共工具提供商商信息"""
        self.api_tool_service.delete_api_tool_provider(provider_id)
        return success_message("删除自定义API供应者成功")

    def get_api_tool_providers_with_page(self):
        """获取API工具提供者列表信息，支持分页"""
        req = GetApiToolProvidersWithPageReq(request.args)
        if not req.validate():
            return validate_error_json(req.errors)

        api_tool_providers, paginator = self.api_tool_service.get_api_tool_provider_with_page(req)
        resp = GetApiToolProvidersWithPageResp(many=True)
        return success_json(PageModel(list=resp.dump(api_tool_providers), paginator=paginator))

    def update_api_tool_provider(self, provider_id: uuid.UUID):
        """更新自定义API工具提供者信息"""
        req = UpdateApiToolProviderReq()
        if not req.validate():
            return validate_error_json(req.errors)
        self.api_tool_service.update_api_tool_provider(provider_id, req)
        return success_message("更新自定义API插件成功")
