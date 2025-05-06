# coding: utf-8
from core.filesys.interface import FileInterface
from middleware.auth import require_roles, get_current_user_uuid
from utils import minio_client, AsyncDatabaseManagerInstance
from utils.response_util import ResponseUtil
from models.enums import Bucket, UserRoleType
from models.fields import FileListModel, FileNameUploadModel
from config import app_config
import time
import uuid
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Request
from fastapi.responses import StreamingResponse
from starlette import status
from io import BytesIO
fileSys_router = APIRouter(prefix="/filesys", tags=["filesys"])


@fileSys_router.post("/upload")
@require_roles(UserRoleType.FORBID)
async def upload_file(request: Request, file: UploadFile = File(...)):
    try:
        out_dict = {
            "file_id": "",
            "file_name": "",
            "file_url": "",
            "file_type": "",
            "status": 0,
        }
        content = await file.read()
        file_name = file.filename
        current_date = datetime.now()
        timestamp = int(time.time())
        file_id = uuid.uuid4().hex
        obj_name = f"{current_date.year}/{current_date.month:02d}/{current_date.day:02d}/{file_id}_{timestamp}_{file_name}"
        result = minio_client.put(bucket_name=Bucket.public_bucket.value, file_name=obj_name, data=BytesIO(content))
        if not result:
            out_dict.update(
                {
                    "status": 0,
                    "file_name": file_name
                }
            )
        else:
            file_url = app_config.file_sys_config.base_url + Bucket.public_bucket.value + "/" + obj_name
            user_id = get_current_user_uuid(request)
            async with AsyncDatabaseManagerInstance.get_session() as session:
                await FileInterface.add(
                    session=session, **{
                        "bucket_name": Bucket.public_bucket.value,
                        "id": file_id,
                        "file_name": file_name,
                        "obj_name": obj_name,
                        "file_url": file_url,
                        "user_id": user_id
                    }
                )
                out_dict.update(
                    {
                        "file_id": file_id,
                        "file_name": file_name,
                        "file_url": file_url,
                        "file_type": file_name.split(".")[-1],
                        "status": 1
                    }
                )
        return ResponseUtil.success(data=out_dict, message="上传接口调用成功！")
    except Exception as e:
        return ResponseUtil.error(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@fileSys_router.get("/get/{file_id}")
@require_roles(UserRoleType.FORBID)
async def get_file(request: Request, file_id: str):
    try:
        async with AsyncDatabaseManagerInstance.get_session() as session:
            _result = await FileInterface.list(
                session=session,
                file_id_list=[file_id]
            )
            search_dict = dict()
            for file in _result:
                search_dict.update(
                    {
                        "bucket_name": file.bucket_name,
                        "obj_name": file.obj_name,
                        "file_name": file.file_name,
                    }
                )
        if not search_dict:
            return ResponseUtil.error(
                message="文件未找到",
                status_code=status.HTTP_200_OK,
            )
        result = minio_client.get(bucket_name=search_dict["bucket_name"], object_name=search_dict["obj_name"])
        if result:
            file_data = BytesIO(result.data)
            file_size = result.getheader("Content-Length")
            return StreamingResponse(
                file_data,
                media_type="application/octet-stream",
                headers={
                    "Content-Disposition": f"attachment; filename={search_dict['file_name']}",
                    "Content-Length": file_size
                }
            )
        else:
            return ResponseUtil.error(
                message="文件未找到",
                status_code=status.HTTP_200_OK,
            )
    except Exception as e:
        return ResponseUtil.error(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@fileSys_router.post("/list")
@require_roles(UserRoleType.FORBID)
async def list_files(request: Request, params: FileListModel):
    try:
        async with AsyncDatabaseManagerInstance.get_session() as session:
            result = await FileInterface.list(
                session=session,
                file_id_list=params.file_id_list
            )
            out_info = list()
            for res in result:
                out_info.append(
                    {
                        "id": res.id,
                        "file_name": res.file_name,
                        "file_url": res.file_url,
                        "file_type": res.file_name.split(".")[-1],
                        "create_time": res.create_time
                    }
                )
            return ResponseUtil.success(data=out_info, message="查询成功！")
    except Exception as e:
        return ResponseUtil.error(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@fileSys_router.put("/update")
@require_roles(UserRoleType.FORBID)
async def update_file(request: Request, params: FileNameUploadModel):
    try:
        async with AsyncDatabaseManagerInstance.get_session() as session:
            result = await FileInterface.list(
                session=session,
                file_id_list=[params.file_id]
            )
            search_dict = dict()
            for file in result:
                search_dict.update(
                    {
                        "bucket_name": file.bucket_name,
                        "file_name": file.file_name,
                        "file_url": file.file_url,
                        "obj_name": file.obj_name
                    }
                )
            current_date = datetime.now()
            new_obj_name = f"{current_date.year}/{current_date.month:02d}/{current_date.day:02d}/{file.id}_{int(time.time())}_{params.file_name}"
            res = minio_client.rename_file(search_dict["bucket_name"], file.obj_name, new_obj_name)
            if res:
                await FileInterface.update(
                    session=session,
                    file_id=params.file_id,
                    file_name=params.file_name,
                    obj_name=new_obj_name
                )
                return ResponseUtil.success(data=params.file_id, message="重命名成功！")
            else:
                return ResponseUtil.error(
                    message="重命名失败！",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
    except Exception as e:
        return ResponseUtil.error(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@fileSys_router.delete("/delete/")
@require_roles(UserRoleType.FORBID)
async def delete_file(request: Request, params: FileListModel):
    try:
        user_id = get_current_user_uuid(request)
        async with AsyncDatabaseManagerInstance.get_session() as session:
            result = await FileInterface.list(
                session=session,
                file_id_list=params.file_id_list
            )
            for file in result:
                minio_client.delete(bucket_name=file.bucket_name, obj_name=file.obj_name)
                await FileInterface.delete(session=session, model_id=file.id, user_id=user_id)
        return ResponseUtil.success(
            data="",
            message="文件删除成功",
        )
    except Exception as e:
        return ResponseUtil.error(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
