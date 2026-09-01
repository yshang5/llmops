"""
  @File    : agent_queue_manager.py
  @Author  : Yue
  @Date    : 2026/8/30 21:25
  @Desc    : 
"""
import queue
import time
import uuid
from queue import Queue
from typing import Generator
from uuid import UUID

from redis import Redis

from internal.core.agent.entities.queue_entity import QueueEvent, AgentThought
from internal.entity.conversation_entity import InvokeFrom


class AgentQueueManager:
    """智能体队列管理器"""
    q: Queue
    user_id: UUID
    task_id: UUID
    invoke_from: InvokeFrom
    redis_client: Redis

    def __init__(self, user_id: UUID, task_id: UUID, invoke_from: InvokeFrom, redis_client: Redis):
        # 1.初始化数据
        self.q = Queue()
        self.user_id = user_id
        self.task_id = task_id
        self.invoke_from = invoke_from
        self.redis_client = redis_client

        # 2. 生产不同的缓存前缀，（根据用户类型生成）debugger/app.service_api
        user_prefix = "account" if invoke_from in [InvokeFrom.WEB_APP, InvokeFrom.DEBUGGER] else "end-user"
        # 3. 设置任务对应的缓存键，代表这次任务已经开始
        self.redis_client.setex(
            self.generate_task_belong_cache_key(task_id),
            1800,
            f"{user_prefix}-{str(user_id)}",
        )

    @classmethod
    def generate_task_belong_cache_key(cls, task_id: UUID) -> str:
        """生成任务的缓存间"""
        return f"generate_task_belong:{str(task_id)}"

    @classmethod
    def generate_task_stopped_cache_key(cls, task_id: UUID) -> str:
        """生成任务的缓存间"""
        return f"generate_stopped_belong:{str(task_id)}"

    def listen(self) -> Generator:
        """监听队列返回的生成式数据"""
        # 1. 定义基础数据 记录超时时间、开始时间、最后一次ping通时间
        listen_timeout = 60
        start_time = time.time()
        last_ping_time = 0

        # 2.创建循环读取队列数据，直到超时或者数据读取完毕
        while True:
            try:
                # 3.从队列中提取数据，验证数据是否存在，如果存在用yield返回
                item = self.q.get(timeout=1)
                if item is None:
                    break
                yield item
            except queue.Empty:
                continue
            finally:
                # 4. 计算获取计算的总耗时
                elapsed_time = time.time() - start_time
                # 5.每10秒发送一个ping请求
                if elapsed_time // 10 > last_ping_time:
                    self.publish(AgentThought(
                        id=uuid.uuid4(),
                        task_id=self.task_id,
                        event=QueueEvent.PING,
                    ))
                    last_ping_time = elapsed_time // 10
                # 6.判断总耗时是否超时，如果超时则往队列中添加超时时间
                if elapsed_time >= listen_timeout:
                    self.publish(AgentThought(
                        id=uuid.uuid4(),
                        task_id=self.task_id,
                        event=QueueEvent.TIMEOUT,
                    ))
                # 7. 检测是否停止，如果停止就添加停止时间
                if self._is_stopped():
                    self.publish(AgentThought(
                        id=uuid.uuid4(),
                        task_id=self.task_id,
                        event=QueueEvent.STOP,
                    ))

    def _is_stopped(self) -> bool:
        """检测任务是否停止"""
        task_stopped_cache_key = self.generate_task_stopped_cache_key(self.task_id)
        result = self.redis_client.get(task_stopped_cache_key)
        return result is not None

    def stop_listen(self) -> None:
        """停止监听队列数据"""
        self.q.put(None)

    def publish(self, agent_queue_event: AgentThought):
        """发布时间信息到队列"""
        # 1. 将时间添加到队列中
        self.q.put(agent_queue_event)
        # 2. 检测事件类型是否为需要停止的类型
        if agent_queue_event.event in [QueueEvent.STOP, QueueEvent.ERROR, QueueEvent.TIMEOUT, QueueEvent.AGENT_END]:
            self.stop_listen()

    def public_error(self, error) -> None:
        self.publish(AgentThought(
            id=uuid.uuid4(),
            task_id=self.task_id,
            event=QueueEvent.ERROR,
            observation=str(error),
        ))
