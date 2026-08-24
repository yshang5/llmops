"""
  @File    : api_tool_service.py
  @Author  : Yue
  @Date    : 2026/5/21 04:09
  @Desc    : 
"""
import json
import uuid
from uuid import UUID

from injector import inject
from dataclasses import dataclass

from numba.scripts.generate_lower_listing import description
from sqlalchemy import desc

from internal.core.tools.api_tools.entities import ToolEntity
from internal.exception import ValidateErrorException, NotFoundException
from internal.core.tools.api_tools.entities.openapi_schema import OpenAPISchema
from internal.model import ApiToolProvider, ApiTool
from internal.schema.api_tool_schema import CreateApiToolReq, GetApiToolProvidersWithPageReq, UpdateApiToolProviderReq
from internal.service.base_service import BaseService
from pkg.sqlalchemy import SQLAlchemy
from pkg.paginator import Paginator
from internal.core.tools.api_tools.providers.api_provider_manager import ApiProviderManager


@inject
@dataclass
class ApiToolService(BaseService):
    api_provider_manager: ApiProviderManager
    db: SQLAlchemy

    @classmethod
    def parse_openapi_schema(cls, openapi_schema_str: str) -> OpenAPISchema:
        """解析传递的openapi_schema字符串，如果出错则抛出错误"""
        try:
            data = json.loads(openapi_schema_str.strip())
            if not isinstance(data, dict):
                raise
        except Exception as e:
            raise ValidateErrorException("传递数据必须是符合OpenAPI规范的JSON字符串")
        return OpenAPISchema(**data)

    def create_api_tool(self, req: CreateApiToolReq) -> None:
        """根据传递的请求创建工具"""
        # todo: 等到授权认证模块完成
        account_id = "3ae06752-40dc-48ed-9bd0-a265319d9db0"
        # 1. 校验并提取openapi_schema
        openapi_schema = self.parse_openapi_schema(req.openapi_schema.data)
        # 2. 查询当前登录哦的账号是否已经创建了同名的工具提供者
        api_tool_provider = self.db.session.query(ApiToolProvider).filter_by(
            account_id=account_id,
            name=req.name.data
        ).one_or_none()

        if api_tool_provider:
            raise ValidateErrorException(f"该工具提供者名字{req.name.data}已经存在")

        # 4. 首先创建工具提供者再创建工具
        api_tool_provider = self.create(
            ApiToolProvider,
            account_id=account_id,
            name=req.name.data,
            icon=req.icon.data,
            description=openapi_schema.description,
            openapi_schema=req.openapi_schema.data,
            headers=req.headers.data,
        )

        # 5. 创建api工具并关联api_tool_provider
        for path, path_item in openapi_schema.paths.items():
            for method, method_item in path_item.items():
                self.create(
                    ApiTool,
                    account_id=account_id,
                    provider_id=api_tool_provider.id,
                    name=method_item.get("operationId"),
                    description=method_item.get("description"),
                    url=f"{openapi_schema.server}{path}",
                    method=method,
                    parameters=method_item.get("parameters", []),
                )

    def get_api_tool_provider(self, provider_id: uuid.UUID) -> ApiToolProvider:
        account_id = "3ae06752-40dc-48ed-9bd0-a265319d9db0"

        api_tool_provider = self.get(ApiToolProvider, provider_id)
        if api_tool_provider is None or str(api_tool_provider.account_id) != account_id:
            raise NotFoundException("该工具提供者不存在")
        return api_tool_provider

    def get_api_tool(self, provider_id: UUID, tool_name: str) -> ApiTool:
        account_id = "3ae06752-40dc-48ed-9bd0-a265319d9db0"
        api_tool = self.db.session.query(ApiTool).filter_by(
            provider_id=provider_id,
            name=tool_name,
            account_id=account_id,
        ).one_or_none()
        if api_tool is None:
            raise NotFoundException("该工具不存在")
        return api_tool

    def delete_api_tool_provider(self, provider_id: uuid.UUID):
        """根据传递的provider_id删除对应的工具提供商+工具的所有信息"""
        account_id = "3ae06752-40dc-48ed-9bd0-a265319d9db0"
        api_tool_provider = self.get(ApiToolProvider, provider_id)

        if api_tool_provider is None or str(api_tool_provider.account_id) != account_id:
            raise NotFoundException("该工具不存在")

        with self.db.auto_commit():
            self.db.session.query(ApiTool).filter(
                ApiTool.provider_id == api_tool_provider.id,
                ApiTool.account_id == account_id,
            ).delete()
            self.db.session.delete(api_tool_provider)

    def get_api_tool_provider_with_page(self, req: GetApiToolProvidersWithPageReq) -> tuple:
        """获取自定义API工具服务提供者分页列表数据"""
        account_id = "3ae06752-40dc-48ed-9bd0-a265319d9db0"

        # 1. 构建一个分页查询器
        paginator = Paginator(db=self.db, req=req)
        # 2. 构建筛选器
        filters = [ApiToolProvider.account_id == account_id]
        if req.search_word.data:
            filters.append(ApiToolProvider.name.ilike(f"%{req.search_word.data}%"))
        # 3. 执行分页并获取数据
        api_tool_providers = paginator.paginate(
            self.db.session.query(ApiToolProvider).filter(*filters).order_by(desc("created_at")),
        )
        return api_tool_providers, paginator

    def update_api_tool_provider(self, provider_id: UUID, req: UpdateApiToolProviderReq):
        """根据传递的provider_id + req更新对应的API工具提供者信息"""
        account_id = "3ae06752-40dc-48ed-9bd0-a265319d9db0"
        api_tool_provider = self.get(ApiToolProvider, provider_id)
        if api_tool_provider is None or str(api_tool_provider.account_id) != account_id:
            raise NotFoundException("该工具不存在")

        openapi_schema = self.parse_openapi_schema(req.openapi_schema.data)
        # 检测当前账号是否已经创建了同名的工具提供者，如果是则抛出错误
        check_api_tool_provider = self.db.session.query(ApiToolProvider).filter(
            ApiToolProvider.id == api_tool_provider.id,
            ApiToolProvider.name == req.name.data,
            ApiToolProvider.id != api_tool_provider.id,
        ).one_or_none()
        if check_api_tool_provider:
            raise ValidateErrorException(f"该工具提供者名字{req.name.data}已经存在")

        with self.db.auto_commit():
            # 先删除该工具提供者下的所有工具
            self.db.session.query(ApiTool).filter(
                ApiTool.provider_id == provider_id,
                ApiTool.account_id == account_id,
            ).delete()

        self.update(
            api_tool_provider,
            name=req.name.data,
            icon=req.icon.data,
            headers=req.headers.data,
            openapi_schema=req.openapi_schema.data,
            description=openapi_schema.description,
        )
        # 新增工作信息而完成覆盖信息
        for path, path_item in openapi_schema.paths.items():
            for method, method_item in path_item.items():
                self.create(
                    ApiTool,
                    account_id=account_id,
                    provider_id=api_tool_provider.id,
                    name=method_item.get("operationId"),
                    description=method_item.get("description"),
                    url=f"{openapi_schema.server}{path}",
                    method=method,
                    parameters=method_item.get("parameters", []),
                )

    def api_tool_invoke(self):
        tool_id = "725eff31-619b-4f5e-ac9a-b40dc553a924"
        api_tool = self.get(ApiTool, tool_id)
        api_tool_provider = api_tool.provider

        tool = self.api_provider_manager.get_tool(
            ToolEntity(
                id=str(api_tool_provider.id),
                name=api_tool.name,
                url=api_tool.url,
                method=api_tool.method,
                description=api_tool.description,
                headers=api_tool_provider.headers,
                parameters=api_tool.parameters,
            )
        )
        return tool.invoke({"q": "love", "doctype": "json"})
