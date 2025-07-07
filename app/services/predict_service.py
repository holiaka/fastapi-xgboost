import xgboost as xgb
import numpy as np
from app.schemas.predict import PredictInput

class PredictService:
    def __init__(self):
        self.model = xgb.XGBRegressor()
        self.model.load_model("models/model.json")

    def predict(self, data: PredictInput):
        features = np.array([[float(data.sp), float(data.origin), data.h, data.dbh, data.ba]])
        prediction = self.model.predict(features)
        return {"prediction": prediction.tolist()}
