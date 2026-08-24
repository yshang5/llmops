"""
  @File    : document_handler.py
  @Author  : Yue
  @Date    : 2026/8/19 13:58
  @Desc    : 
"""
from uuid import UUID

from injector import inject
from dataclasses import dataclass
from flask import request

from internal.schema.document_schema import CreateDocumentsReq, CreateDocumentsResp, GetDocumentResp, \
    UpdateDocumentNameReq, GetDocumentsWithPageResp, GetDocumentsWithPageReq, UpdateDocumentEnabledReq
from internal.service import DocumentService
from pkg.paginator import PageModel
from pkg.response import validate_error_json, success_json, success_message


@inject
@dataclass
class DocumentHandler:
    """文档处理器"""
    document_service: DocumentService

    def create_documents(self, dataset_id: UUID):
        """知识库新增/上传文档列表"""
        # 1.提取请求并校验
        req = CreateDocumentsReq()
        if not req.validate():
            return validate_error_json(req.errors)
        # 2. 调用服务并创建文档，返回文档列表信息+处理批次
        documents, batch = self.document_service.create_documents(dataset_id, **req.data)
        # 3. 生成响应结构体并返回
        resp = CreateDocumentsResp()
        return success_json(resp.dump((documents, batch)))

    def get_documents_status(self, dataset_id: UUID, batch: str):
        """根据传递的知识库id+批处理标识获取文档的状态"""
        documents_status = self.document_service.get_documents_status(dataset_id, batch)
        return success_json(documents_status)

    def get_document(self, dataset_id: UUID, document_id: UUID):
        """根据传递的知识库id + 文档id获取文档详情信息"""
        document = self.document_service.get_document(dataset_id, document_id)
        res = GetDocumentResp()
        return success_json(res.dump(document))

    def update_document_name(self, dataset_id: UUID, document_id: UUID):
        """根据传递的知识库id + 文档id更新对应文档的名称信息"""
        # 1.提取请求 并校验数据
        req = UpdateDocumentNameReq()
        if not req.validate():
            return validate_error_json(req.errors)
        self.document_service.update_document(dataset_id, document_id, name=req.name.data)
        return success_message("更新文档名称成功")

    def get_documents_with_page(self, dataset_id: UUID):
        """根据传递的知识库id获取文档分页列表数据"""
        req = GetDocumentsWithPageReq(request.args)
        if not req.validate():
            return validate_error_json(req.errors)
        documents, paginator = self.document_service.get_documents_with_page(dataset_id, req)
        resp = GetDocumentsWithPageResp(many=True)
        return success_json(PageModel(list=resp.dump(documents), paginator=paginator))

    def update_document_enabled(self, dataset_id: UUID, document_id: UUID):
        """根据传递的知识库id + 文档id 更新指定文档的开启或关闭"""
        req = UpdateDocumentEnabledReq()
        if not req.validate():
            return validate_error_json(req.errors)
        self.document_service.update_document_enabled(dataset_id, document_id, req.enabled.data)
        return success_message("更改文档启用状态成功")

    def delete_document(self, dataset_id: UUID, document_id: UUID):
        """删除文档"""
        self.document_service.delete_document(dataset_id, document_id)
        return success_message("删除文档成功")
