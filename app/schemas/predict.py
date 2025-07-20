from pydantic import BaseModel


class PredictInput(BaseModel):
    sp: int
    origin: int
    h: float
    dbh: float
    ba: float
