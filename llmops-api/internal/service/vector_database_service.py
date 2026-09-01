"""
  @File    : vector_database_service.py
  @Author  : Yue
  @Date    : 2026/4/18 20:26
  @Desc    : 
"""
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_weaviate import WeaviateVectorStore
from injector import inject
from weaviate import WeaviateClient
import weaviate
import os

from weaviate.collections import Collection

from internal.service.embeddings_service import EmbeddingsService

# 向量数据库的集合名字
COLLECTION_NAME = "Dataset"


@inject
class VectorDatabaseService:
    """向量数据库服务"""
    vector_store: WeaviateVectorStore
    client: WeaviateClient
    embeddings_service: EmbeddingsService

    def __init__(self, embeddings_services: EmbeddingsService):
        """初始化，完成weaviate客户端和langchain向量数据库实例创建"""
        self.client = weaviate.connect_to_local(host=os.getenv("WEAVIATE_HOST"), port=int(os.getenv("WEAVIATE_PORT")))
        self.embeddings_service = embeddings_services
        self.vector_store = WeaviateVectorStore(
            client=self.client,
            index_name=COLLECTION_NAME,
            text_key="text",
            embedding=self.embeddings_service.embeddings,
        )

    @classmethod
    def combine_documents(cls, documents: list[Document]) -> str:
        """将对应的文本列表使用换行符进行合并"""
        return "\n\n".join([document.page_content for document in documents])

    def get_retriever(self) -> VectorStoreRetriever:
        return self.vector_store.as_retriever()

    @property
    def collection(self) -> Collection:
        return self.client.collections.get(COLLECTION_NAME)
