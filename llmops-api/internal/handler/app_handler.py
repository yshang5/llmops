# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
  @File    : app_handler.py.py
  @Author  : Yue
  @Date    : 2026/3/24
  @Desc    :
"""
import logging
import os
import uuid
from dataclasses import dataclass
from operator import itemgetter
from queue import Queue
from threading import Thread
from typing import Dict, Any, Literal, Generator
from uuid import UUID

from injector import inject
from langchain_core.memory import BaseMemory
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain_core.messages import ToolMessage, AIMessageChunk
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate, \
    SystemMessagePromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableConfig
from langchain_core.tracers import Run
from langchain_openai import ChatOpenAI
from langgraph.constants import END
from langgraph.graph import MessagesState, StateGraph
from redis import Redis

from internal.core.agent.entities.agent_entity import AgentConfig
from internal.entity.conversation_entity import InvokeFrom
from internal.schema.app_schema import CompletionReq
from internal.service import AppService, VectorDatabaseService, ApiToolService, ConversationService
from pkg.response import *
import json
from internal.core.tools.builtin_tools.providers import BuiltinProviderManager
from internal.core.agent.agents import FunctionCallAgent, AgentQueueManager


@inject
@dataclass
class AppHandler:
    """应用控制器"""

    app_service: AppService
    vector_database_service: VectorDatabaseService
    provider_factory: BuiltinProviderManager
    api_tool_service: ApiToolService
    builtin_provider_manager: BuiltinProviderManager
    conversation_service: ConversationService
    redis_client: Redis

    @classmethod
    def _load_memory_variables(cls, input: Dict[str, Any], config: RunnableConfig) -> Dict[str, Any]:
        """加载记忆变量信息"""
        configurable = config.get("configurable", {})
        configurable_memory = configurable.get("memory", None)
        if configurable_memory is not None and isinstance(configurable_memory, BaseMemory):
            return configurable_memory.load_memory_variables(input)
        return {"history": ""}

    @classmethod
    def _save_context(cls, run_obj: Run, config: RunnableConfig) -> None:
        configurable = config.get("configurable", {})
        configurable_memory = configurable.get("memory", None)
        if configurable_memory is not None and isinstance(configurable_memory, BaseMemory):
            configurable_memory.save_context(run_obj.inputs, run_obj.outputs)

    def ping(self):
        pass

    def debug(self, app_id: UUID):
        """应用会话调试聊天接口"""
        # 1.提取从接口中获取的输出，post
        req = CompletionReq()
        if not req.validate():
            return validate_error_json(req.errors)

        tools = [
            self.builtin_provider_manager.get_tool("google", "google_serper")(),
            self.builtin_provider_manager.get_tool("gaode", "gaode_weather")(),
            self.builtin_provider_manager.get_tool("dalle", "dalle3")(),
        ]

        agent = FunctionCallAgent(
            AgentConfig(
                llm=ChatOpenAI(model="gpt-4o-mini"),
                enable_long_term_memory=True,
                tools=tools,
            ),
            AgentQueueManager(
                user_id=uuid.uuid4(),
                task_id=uuid.uuid4(),
                invoke_from=InvokeFrom.DEBUGGER,
                redis_client=self.redis_client
            )
        )

        def stream_event_response() -> Generator:
            """流式事件输出响应"""
            for agent_queue_event in agent.run(req.query.data, [], ""):
                data = {
                    "id": str(agent_queue_event.id),
                    "task_id": str(agent_queue_event.task_id),
                    "event": agent_queue_event.event,
                    "observation": agent_queue_event.observation,
                    "thought": agent_queue_event.thought,
                    "tool": agent_queue_event.tool,
                    "tool_input": agent_queue_event.tool_input,
                    "latency": agent_queue_event.latency,
                }
                yield f"event: {agent_queue_event.event}\ndata: {json.dumps(data)}\n\n"

        return compact_generate_response(stream_event_response())

    def _debug(self, app_id: UUID):
        """chat interface"""
        req = CompletionReq()
        query = req.query.data
        if not req.validate():
            return validate_error_json(req.errors)
        system_prompt = "你是一个强大的AI机器人，能根据对应的上下文和历史对话信息回复用户的问题\n\n<context>{context}</context>"
        prompt_template = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(system_prompt),
                MessagesPlaceholder("history"),
                HumanMessagePromptTemplate.from_template("{query}")
            ]
        )
        memory = ConversationBufferWindowMemory(
            k=10,
            input_key="query",
            output_key="output",
            return_messages=True,
            chat_memory=FileChatMessageHistory("./storage/memory/chat_history.txt")
        )

        llm = ChatOpenAI(
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-5.4-nano"
        )
        parser = StrOutputParser()

        retriever = self.vector_database_service.get_retriever() | RunnableLambda(
            lambda documents: self.vector_database_service.combine_documents(documents)
        )
        chain = (
            (RunnablePassthrough.assign(
                history=RunnableLambda(self._load_memory_variables) | itemgetter("history"),
                context=itemgetter("query") | retriever
            ) | prompt_template | llm | parser)
            .with_listeners(
                on_end=self._save_context
            )
        )
        chain_input = {"query": query}
        content = chain.invoke(chain_input, config=RunnableConfig(
            configurable={"memory": memory}
        ))
        return success_json({"content": content})

    def create_app(self):
        app = self.app_service.create_app()
        return success_message(f"app created successfully: {app.id}")

    def get_app(self, id: uuid.UUID):
        app = self.app_service.get_app(id)
        return success_json(f"app got successfully: {app.name}")

    def update_app(self, id: uuid.UUID):
        app = self.app_service.update_app(id)
        return success_json(f"app updated successfully: {app.name}")

    def delete_app(self, id: uuid.UUID):
        app = self.app_service.delete_app(id)
        return success_json(f"app deleted successfully: {app.id}")
