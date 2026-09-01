"""
  @File    : dataset_task.py
  @Author  : Yue
  @Date    : 2026/8/25 18:33
  @Desc    : 
"""
from uuid import UUID

from celery import shared_task


@shared_task
def delete_dataset(dataset_id: UUID):
    """根据传递的知识库id删除特定的知识库信息"""
    from app.http.module import injector
    from internal.service import IndexingService

    indexing_service = injector.get(IndexingService)
    indexing_service.delete_dataset(dataset_id)
