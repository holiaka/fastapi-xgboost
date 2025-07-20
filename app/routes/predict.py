from fastapi import APIRouter, Depends
from app.utils.security import get_current_user
from app.schemas.predict import PredictInput
from app.models.user import User
from app.services.predict_service import PredictService

router = APIRouter(prefix="/predict", tags=["predict"])


@router.post("/biomass", summary="Make prediction biomass with XGBoost")
def predict(input_data: PredictInput, user: User = Depends(get_current_user)):
    return PredictService().predict(input_data)
