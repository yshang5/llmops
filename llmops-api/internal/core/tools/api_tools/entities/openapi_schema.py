"""
  @File    : openapi_schema.py
  @Author  : Yue
  @Date    : 2026/5/21 04:20
  @Desc    : 
"""
from pydantic import BaseModel, Field, field_validator

from internal.exception import ValidateErrorException
from enum import Enum


class ParameterIn(str, Enum):
    """参数支持存放的位置"""
    PATH = "path"
    QUERY = "query"
    HEADER = "header"
    COOKIE = "cookie"
    REQUEST_BODY = "request_body"


class ParameterType(str, Enum):
    """参数支持的类型"""
    STR = "str"
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"


ParameterTypeMap = {
    ParameterType.STR: str,
    ParameterType.INT: int,
    ParameterType.FLOAT: float,
    ParameterType.BOOL: bool,
}


class OpenAPISchema(BaseModel):
    """openAPI规范的数据结构"""
    description: str = Field(default="", validate_default=True, description="工具提供这的描述信息")
    server: str = Field(default="", validate_default=True, description="工具提供这的描述信息")
    paths: dict[str, dict] = Field(default_factory=dict, validate_default=True,
                                   description="工具提供这的路径参数字典")

    @field_validator("server", mode="before")
    def validate_server(cls, server: str) -> str:
        if server is None or server == "":
            raise ValidateErrorException("server不能为空且为字符串")
        return server

    @field_validator("description", mode="before")
    def validate_description(cls, description: str) -> str:
        if description is None or description == "":
            raise ValidateErrorException("server不能为空且为字符串")
        return description

    @field_validator("paths", mode="before")
    def validate_paths(cls, paths: dict[str, dict]) -> dict[str, dict]:
        """校验paths信息，涵盖：方法提取、operationId唯一标识，parameters校验"""
        # 1. 不能为空且类型应该对得上
        if not paths or not isinstance(paths, dict):
            raise ValidateErrorException("server不能为空且为字符串")

        # 2. 提取paths中的每个元素，并且获取元素下的get/post方法对应的值
        methods = ["get", "post"]
        interfaces = []
        extra_paths = {}
        for path, path_item in paths.items():
            for method in methods:
                # 3. 检测是否存在特定的方法并提取信息
                if method in path_item:
                    interfaces.append({
                        "path": path,
                        "method": method,
                        "operation": path_item[method],
                    })

        # 4. 遍历所有的接口并且校验信息，包括operationId是否是唯一的，parameters参数
        operation_ids = set()
        for interface in interfaces:
            if not isinstance(interface["operation"].get("description"), str):
                raise ValidateErrorException("description必须不为空且为字符串")
            operation_id = interface["operation"].get("operationId")
            if not isinstance(operation_id, str):
                raise ValidateErrorException("operationId必须不为空且为字符串")
            if not isinstance(interface["operation"].get("parameters", []), list):
                raise ValidateErrorException("parameters必须为空或者列表")
            if operation_id in operation_ids:
                raise ValidateErrorException(f"operationId必须唯一，重复id: {operation_id}")
            operation_ids.add(operation_id)

            for parameter in interface["operation"].get("parameters", []):
                if not isinstance(parameter.get("name"), str):
                    raise ValidateErrorException("parameter.name参数必须为字符串且不为空")
                if not isinstance(parameter.get("description"), str):
                    raise ValidateErrorException("parameter.description参数必须为字符串且不为空")
                if not isinstance(parameter.get("required"), bool):
                    raise ValidateErrorException("parameter.required参数必须为字符串且不为空")
                if (
                        not isinstance(parameter.get("in"), str)
                        or
                        parameter.get("in") not in ParameterIn.__members__.values()
                ):
                    raise ValidateErrorException(f"parameter.in参数必须为{'/'.join([item for item in ParameterIn])}")
                if (
                        not isinstance(parameter.get("type"), str)
                        or
                        parameter.get("type") not in ParameterType.__members__.values()
                ):
                    raise ValidateErrorException(
                        f"parameter.type参数必须为{'/'.join([item for item in ParameterType])}")
            # 组装并更新
            extra_paths[interface["path"]] = {
                interface["method"]: {
                    "description": interface["operation"]["description"],
                    "operationId": interface["operation"]["operationId"],
                    "parameters": [{
                        "name": parameter.get("name"),
                        "in": parameter.get("in"),
                        "description": parameter.get("description"),
                        "required": parameter.get("required"),
                        "type": parameter.get("type"),
                    } for parameter in interface["operation"].get("parameters", [])],
                }
            }
        return extra_paths
