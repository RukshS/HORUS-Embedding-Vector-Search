from pydantic import BaseModel, Field, HttpUrl
from bson import ObjectId

class Module(BaseModel):
    module_id: str | None = None
    module_name: str
    is_core: bool = True
    module_domain: str | None = None
    description: str = Field(default="", description="Detailed description of the module")
    thumbnail_url: HttpUrl | None = Field(default=None, description="URL to the thumbnail image")

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class ModuleQuery(BaseModel):
    query: str
    