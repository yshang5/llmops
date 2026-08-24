"""
  @File    : cos_service.py
  @Author  : Yue
  @Date    : 2026/8/17 14:25
  @Desc    : 
"""
import hashlib
import uuid
from datetime import datetime

from injector import inject
from dataclasses import dataclass
from werkzeug.datastructures import FileStorage
from qcloud_cos import CosS3Client, CosConfig

from internal.entity.upload_file_entity import ALLOWED_IMAGE_EXTENSION, ALLOWED_DOCUMENT_EXTENSION
from internal.exception import FailException
from internal.model import UploadFile
import os

from internal.service.upload_file_service import UploadFileService


@inject
@dataclass
class CosService:
    """腾讯云cos对象存储服务"""
    upload_file_service: UploadFileService

    def get_file_url(self, key: str) -> str:
        """根据传递的cos云端key获取图片的实际URL地址"""
        cos_domain = os.environ.get("COS_DOMAIN")

        if not cos_domain:
            bucket = os.environ.get("COS_BUCKET")
            scheme = os.environ.get("COS_SCHEME")
            region = os.environ.get("COS_REGION")
            cos_domain = f"{scheme}://{bucket}.cos.{region}.myqcloud.com"
        return f"{cos_domain}/{key}"

    def download_file(self, key: str, target_file_path: str):
        """下载cos云端的文件到本地的指定路径"""
        client = self._get_client()
        bucket = self._get_bucket()

        client.download_file(bucket, key, target_file_path)

    def upload_file(self, file: FileStorage, only_image: bool = False) -> UploadFile:
        """上传文件到腾讯云cos对象存储，上传后返回文件的信息"""
        # todo: 等到授权认证模块完成
        account_id = "3ae06752-40dc-48ed-9bd0-a265319d9db0"
        # 1.提取文件扩展名并检测是否可以上传
        filename = file.filename
        extension = file.filename.rsplit(".", 1)[-1] if "." in file.filename else ""
        if extension.lower() not in (ALLOWED_IMAGE_EXTENSION + ALLOWED_DOCUMENT_EXTENSION):
            raise FailException(f"该.{extension}扩展的文件不允许上传")
        elif only_image and extension.lower() not in ALLOWED_IMAGE_EXTENSION:
            raise FailException(f"该.{extension}扩展的文件不支持上传，请上传正确的图片")
        # 2.获取客户端 + 存储桶名字
        client = self._get_client()
        bucket = self._get_bucket()
        # 3.生成一个随机的名字
        random_filename = str(uuid.uuid4()) + "." + extension
        now = datetime.now()
        upload_filename = f"{now.year}/{now.month:02d}/{now.day:02d}/{random_filename}"

        # 4.流式读取上传的数据并将其上传的cos中
        file_content = file.stream.read()
        # 5.将数据上传到cos中
        try:
            client.put_object(bucket, file_content, upload_filename)
        except Exception as e:
            raise FailException("上传文件失败，请稍后重试")
        # 6.创建upload_file记录
        return self.upload_file_service.create_upload_file(
            account_id=account_id,
            name=filename,
            key=upload_filename,
            size=len(file_content),
            extension=extension,
            mime_type=file.mimetype,
            hash=hashlib.sha3_256(file_content).hexdigest(),
        )

    @classmethod
    def _get_client(cls) -> CosS3Client:
        """获取腾讯云cos对象存储客户端"""
        conf = CosConfig(
            Region=os.environ.get("COS_REGION"),
            SecretId=os.environ.get("COS_SECRET_ID"),
            SecretKey=os.environ.get("COS_SECRET_KEY"),
            Token=None,
            Scheme=os.environ.get("COS_SCHEME", "https"),
        )
        return CosS3Client(conf)

    @classmethod
    def _get_bucket(cls) -> str:
        return os.environ.get("COS_BUCKET")
