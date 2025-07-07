from pydantic import BaseModel

class PredictInput(BaseModel):
    sp: str
    origin: str
    h: float
    dbh: float
    ba: float
