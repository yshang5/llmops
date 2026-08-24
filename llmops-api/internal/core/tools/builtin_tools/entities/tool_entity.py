"""
  @File    : tool_entity.py
  @Author  : Yue
  @Date    : 2026/5/8 20:09
  @Desc    : 
"""
from typing import Optional, Any
from enum import Enum

from pydantic import BaseModel, Field


class ToolParamType(str, Enum):
    """工具参数类型枚举"""
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    SELECT = "select"


class ToolParam(BaseModel):
    """工具参数类型"""
    label: str  # 参数名称
    name: str  # 标签值
    type: ToolParamType  # 参数类型
    required: bool = False
    default: Optional[Any] = None  # 默认值
    min: Optional[float] = None  # 最小值
    max: Optional[float] = None  # 最大值
    options: list[dict[str, Any]] = Field(default_factory=list)  # 下拉菜单选项列表


class ToolEntity(BaseModel):
    """工具实体类，存储的信息映射的是工具名.yaml里的数据"""
    name: str  # 名字
    label: str  # 工具标签
    description: str  # 工具描述
    params: list[ToolParam] = Field(default_factory=list)  # 工具参数
