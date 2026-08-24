"""
  @File    : tool_entity.py
  @Author  : Yue
  @Date    : 2026/6/1 16:13
  @Desc    : 
"""
from pydantic import BaseModel, Field


class ToolEntity(BaseModel):
    """API实体工具信息，记录了创建LangChain工具所需的配置信息"""
    id: str = Field(default="", description="api工具提供者对应的id")
    name: str = Field(default="", description="api工具的名称")
    url: str = Field(default="", description="api工具发起请求的URL地址")
    method: str = Field(default="get", description="api工具发起请求的方法，只支持get和post")
    description: str = Field(default="", description="api工具的描述信息")
    headers: list[dict] = Field(default_factory=list, description="API工具的请求头信息")
    parameters: list[dict] = Field(default_factory=list, description="API工具的参数列表信息")
