from pydantic import BaseModel
from typing import TypeVar, Generic

T = TypeVar("T")


class Result(Generic[T], BaseModel):
    success: bool
    err_code: str = None
    err_msg: str = None
    data: T = None

    @classmethod
    def success(cls, data: T):
        return Result(success=True, err_code=None, err_msg=None, data=data)

    @classmethod
    def failed(cls, msg):
        return Result(success=False, err_code="E000X", err_msg=msg, data=None)

    @classmethod
    def failed(cls, code, msg):
        return Result(success=False, err_code=code, err_msg=msg, data=None)
