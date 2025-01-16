from fastapi import UploadFile
from pydantic import BaseModel
from typing import Type, TypeVar, List
from io import BytesIO

T = TypeVar('T', bound=BaseModel)


async def sqlalchemy_to_pydantic(
    sqlalchemy_model: Type["OrmBase"],
    pydantic_model: Type[T],
) -> T:
    return pydantic_model.model_validate(sqlalchemy_model, from_attributes=True)


async def many_sqlalchemy_to_pydantic(
    sqlalchemy_models: list[Type["OrmBase"]],
    pydantic_model: Type[T],
) -> List[T]:
    return [await sqlalchemy_to_pydantic(sqlalchemy_model=row, pydantic_model=pydantic_model) for row in sqlalchemy_models]

