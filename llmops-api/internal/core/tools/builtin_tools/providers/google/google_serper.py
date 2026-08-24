"""
  @File    : google_serper.py
  @Author  : Yue
  @Date    : 2026/5/8 19:02
  @Desc    : 
"""
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.tools import BaseTool
from langchain_community.tools import GoogleSerperRun
from pydantic import BaseModel, Field
from internal.lib.helper import add_attribute


class GoogleSerperArgsSchema(BaseModel):
    """各个serperAPI搜索哦参数描述"""
    query: str = Field(description="需要检索查询的语句")


@add_attribute(attr_name="args_schema", attr_value=GoogleSerperArgsSchema)
def google_serper(**kwargs) -> BaseTool:
    """谷歌serper搜索"""
    return GoogleSerperRun(
        name="google_serper",
        description="这是一个低成本的谷歌搜索API。当你需要搜索时事或者一些你认为可能在互联网上获得可信度高的信息时候可以使用该工具，该工具的输入是一个查询语句",
        args_schema=GoogleSerperArgsSchema,  # type: ignore[call-arg]
        api_wrapper=GoogleSerperAPIWrapper()
    )
