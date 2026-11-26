from pydantic import BaseModel

class Tender(BaseModel):
    id: str
    title: str
    institution: str
    city: str | None = None
    category: str
    deadline: str | None = None
    source_name: str
    source_url: str | None = None
    summary: str | None = None
    status: str = "new"
