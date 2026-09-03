from pydantic import BaseModel, Field


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeOut(BaseModel):
    email: str
    full_name: str
    role: str


class ExceptionOut(BaseModel):
    code: str
    kind: str
    title: str
    dollar_impact: float
    recommendation: str
    action: str
    sku_code: str | None
    dc_code: str | None
    plant_code: str | None
    detail: str
    acknowledged: bool = False


class QueueOut(BaseModel):
    week: int
    n: int
    total_impact: float
    exceptions: list[ExceptionOut]


class AckIn(BaseModel):
    code: str = Field(min_length=3)
