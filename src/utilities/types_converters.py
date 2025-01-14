from pydantic import BaseModel
from typing import Type


def sqlalchemy_to_pydantic(
    sqlalchemy_model: Type["OrmBase"],
    pydantic_model: Type[BaseModel],
):
    return pydantic_model.model_validate(sqlalchemy_model, from_attributes=True)


async def many_sqlalchemy_to_pydantic(
    sqlalchemy_models: list[Type["OrmBase"]],
    pydantic_model: Type[BaseModel],
):
    return [sqlalchemy_to_pydantic(sqlalchemy_model=row, pydantic_model=pydantic_model) for row in sqlalchemy_models]


