"""
  @File    : dataset_service.py
  @Author  : Yue
  @Date    : 2026/8/18 12:54
  @Desc    : 
"""
from uuid import UUID

from injector import inject
from dataclasses import dataclass

from internal.schema.dataset_schema import CreateDatasetReq, UpdateDatasetReq, GetDatasetsWithPageReq
from internal.service.base_service import BaseService
from pkg.paginator import Paginator
from pkg.sqlalchemy import SQLAlchemy
from ..exception import ValidateErrorException, NotFoundException
from internal.model import Dataset
from internal.entity.dataset_entity import DEFAULT_DATASET_DESCRIPTION_FORMATTER


@inject
@dataclass
class DatasetService(BaseService):
    """知识库服务"""
    db: SQLAlchemy

    def create_dataset(self, req: CreateDatasetReq) -> Dataset:
        """根据传递的请求信息创建知识库"""
        account_id = "3ae06752-40dc-48ed-9bd0-a265319d9db0"

        # 1.检测该账号下是否存在同名知识库
        dataset = self.db.session.query(Dataset).filter_by(
            account_id=account_id,
            name=req.name.data,
        ).first()

        if dataset:
            raise ValidateErrorException(f"该知识库{req.name.data}已经存在")

        # 2.检测是否传递了描述信息
        if req.description.data is None or req.description.data.strip() == "":
            req.description.data = DEFAULT_DATASET_DESCRIPTION_FORMATTER.format(name=req.name.data)
        # 3.创建知识库记录并返回
        return self.create(
            Dataset,
            account_id=account_id,
            name=req.name.data,
            icon=req.icon.data,
            description=req.description.data,
        )

    def get_dataset(self, dataset_id: UUID) -> Dataset:
        """根据传递的知识库id获取知识库记录"""
        account_id = "3ae06752-40dc-48ed-9bd0-a265319d9db0"

        dataset = self.get(Dataset, dataset_id)
        if dataset is None or str(dataset.account_id) != account_id:
            raise NotFoundException("该知识库不存在")
        return dataset

    def update_dataset(self, dataset_id: UUID, req: UpdateDatasetReq) -> Dataset:
        """根据传递的知识库id和知识库数据更新知识库"""
        account_id = "3ae06752-40dc-48ed-9bd0-a265319d9db0"
        dataset = self.get(Dataset, dataset_id)
        # 1.校验待更新知识库是否存在
        if dataset is None or str(dataset.account_id) != account_id:
            raise NotFoundException("该知识库不存在")
        # 2.校验要更新的知识库名字是否出现重名
        check_dataset = self.db.session.query(Dataset).filter(
            Dataset.account_id == account_id,
            Dataset.name == req.name.data,
            # 如果不是本知识库且有名字一样的 那就报错
            Dataset.id != dataset_id,
        ).one_or_none()
        if check_dataset:
            raise ValidateErrorException(f"该知识库名称{req.name.data}已存在，请修改")

        # 3. 校验描述信息是否为空，如果为空 人为设置默认description
        if req.description.data is None or req.description.data.strip() == "":
            req.description.data = DEFAULT_DATASET_DESCRIPTION_FORMATTER.format(name=req.name.data)

        # 4.更新数据库
        self.update(
            dataset,
            name=req.name.data,
            description=req.description.data,
            icon=req.icon.data,
        )
        return dataset

    def get_datasets_with_page(self, req: GetDatasetsWithPageReq) -> tuple[list[Dataset], Paginator]:
        """根据传递的信息获取知识库列表的分页数据"""
        account_id = "3ae06752-40dc-48ed-9bd0-a265319d9db0"

        # 1. 构建分页查询器
        paginator = Paginator(db=self.db, req=req)

        # 2. 构建筛选器
        filters = [Dataset.account_id == account_id]
        if req.search_word.data:
            filters.append(Dataset.name.ilike(f"%{req.search_word.data}%"))

        # 3. 执行分页查询
        from sqlalchemy import desc
        datasets = paginator.paginate(
            self.db.session.query(Dataset).filter(*filters).order_by(desc("created_at"))
        )
        return datasets, paginator
