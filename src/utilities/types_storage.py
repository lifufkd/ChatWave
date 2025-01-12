from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import Annotated


datetime_type = Annotated[datetime, mapped_column(nullable=True)]
text_type = Annotated[str, mapped_column(nullable=True)]
