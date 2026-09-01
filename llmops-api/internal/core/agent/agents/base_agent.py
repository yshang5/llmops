"""
  @File    : base_agent.py
  @Author  : Yue
  @Date    : 2026/8/30 10:42
  @Desc    : 
"""
from abc import ABC, abstractmethod
from typing import Generator

from langchain_core.messages import AnyMessage

from internal.core.agent.agents import AgentQueueManager
from internal.core.agent.entities.agent_entity import AgentConfig
from internal.core.agent.entities.queue_entity import AgentThought


class BaseAgent(ABC):
    """LLMOps项目基础Agent"""
    agent_config: AgentConfig
    agent_queue_manager: AgentQueueManager

    def __init__(self, agent_config: AgentConfig, agent_queue_manager: AgentQueueManager):
        """构造函数，初始化智能体图结构程序"""
        self.agent_config = agent_config
        self.agent_queue_manager = agent_queue_manager

    @abstractmethod
    def run(
            self,
            query: str,
            history: list[AnyMessage] = None,
            long_term_memory: str = '',
    ) -> Generator[AgentThought, None, None]:
        """智能体运行函数，传递原始提问query、长短期记忆、并调用智能体生成响应内容"""
        raise NotImplementedError("Agent智能体的run函数未实现")
