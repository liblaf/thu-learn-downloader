import pydantic
from pydantic import ConfigDict


class BaseModel(pydantic.BaseModel):
    model_config: ConfigDict = ConfigDict(arbitrary_types_allowed=True)
