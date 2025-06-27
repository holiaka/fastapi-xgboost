from fastapi import FastAPI
from pydantic import BaseModel
import xgboost as xgb
import numpy as np

app = FastAPI()

# Load model (adjust file name and path if needed)
model = xgb.XGBRegressor()
model.load_model("model.json")


# Define the input data format
class Features(BaseModel):
    features: list[float]


@app.get("/")
def root():
    return {"message": "XGBoost model API is running!"}


@app.post("/predict")
def predict(data: Features):
    features_array = np.array([data.features])
    prediction = model.predict(features_array)
    return {"prediction": prediction.tolist()}
