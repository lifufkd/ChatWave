from pydantic import BaseModel, Field, model_validator, field_validator
from typing import Annotated, Optional
from datetime import datetime, date
from utilities import validate_password, validate_nicknames, validate_nicknames_and_ids, request_limit


class CreateGroup(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=64)]
    description: Annotated[Optional[str], Field(None)]