"""
  @File    : token_buffer_memory.py
  @Author  : Yue
  @Date    : 2026/8/29 09:24
  @Desc    : 
"""

from dataclasses import dataclass

from langchain_core.messages import AnyMessage, trim_messages, get_buffer_string
from sqlalchemy import desc
from torch.backends.opt_einsum import strategy

from internal.entity.conversation_entity import MessageStatus
from internal.model.conversation import Conversation, Message
from pkg.sqlalchemy import SQLAlchemy
from langchain_core.language_models import BaseLanguageModel


@dataclass
class TokenBufferMemory:
    """基于token技术的缓冲记忆组件"""
    conversation: Conversation
    db: SQLAlchemy
    model_instance: BaseLanguageModel

    def get_history_prompt_messages(
            self,
            max_token_limit: int = 2000,
            message_limit: int = 10,
    ) -> list[AnyMessage]:
        """根据传递的token限制 + 消息条数限制获取制定会话模型的历史消息列表"""
        # 1. 判断会话模型是否存在，如果不存在直接返回空列表
        if self.conversation is None:
            return []
        # 2. 查询改回画的消息列表，并且使用时间进行倒序排序，同时匹配答案不为空、匹配会话id、没有软删除、状态是正常
        messages = self.db.session.query(Message).filter(
            Message.conversation_id == self.conversation.id,
            Message.answer != "",
            not Message.is_deleted,
            Message.status == MessageStatus.NORMAL,
        ).order_by(desc("created_at")).limit(message_limit).all()
        messages = list(reversed(messages))

        # 3. 将messages转换成langchain消息列表
        prompt_messages = []
        for message in messages:
            from langchain_core.messages import HumanMessage
            prompt_messages.extend([
                HumanMessage(content=message.query),
                HumanMessage(content=message.answer),
            ])

        # 4. 调用langchain集成的trim_messages函数剪切消息列表
        return trim_messages(
            messages=prompt_messages,
            max_tokens=max_token_limit,
            token_counter=self.model_instance,
            strategy="last"
        )

    def get_history_prompt_text(
            self,
            human_prefix: str = "Human",
            ai_prefix: str = "AI",
            max_token_limit: int = 2000,
            message_limit: int = 10,
    ) -> str:
        """根据传递的数据获取指定会话历史消息提示文本（短期记忆的文本形式，用于文本生成模型）"""
        # 1.根据传递的信息获取历史消息列表
        messages = self.get_history_prompt_messages(max_token_limit, message_limit)
        # 2.将消息列表转成文本
        return get_buffer_string(
            messages=messages,
            human_prefix=human_prefix,
            ai_prefix=ai_prefix,
        )
