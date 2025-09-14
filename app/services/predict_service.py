import xgboost as xgb
import numpy as np
import os
from typing import Dict, Tuple
from app.schemas.predict import PredictInput


class PredictService:
    def __init__(self):
        self.model_info = {
            "growing-stock": {
                "file": "01_GS.json",
                "unit": "m³/ha",
                "label": "Growing stock",
            },
            "trunk": {
                "file": "02_M_all_stem.json",
                "unit": "t/ha",
                "label": "Total trunk biomass",
            },
            "trunk-bark": {
                "file": "03_M_stem_bark.json",
                "unit": "t/ha",
                "label": "Trunk bark biomass",
            },
        }
        self.models = self.load_models()

    def load_models(self) -> Dict[str, xgb.XGBRegressor]:
        model_dir = (
            "models/xgboost-models/tree-biomass"  # відносний або абсолютний шлях
        )

        models = {}
        for key, info in self.model_info.items():
            path = os.path.join(model_dir, info["file"])
            model = xgb.XGBRegressor()
            model.load_model(path)
            models[key] = model
        return models

    def predict(self, data: PredictInput) -> Dict[str, Dict[str, str]]:
        features = np.array(
            [[int(data.sp), int(data.origin), data.h, data.dbh, data.ba]]
        )
        results = {}

        for key, model in self.models.items():
            prediction = model.predict(features)
            mean = float(prediction[0])
            ci_lower, ci_upper = self.estimate_confidence_interval(mean)
            results[key] = {
                "label": self.model_info[key]["label"],
                "value": f"{mean:.2f}",
                "unit": self.model_info[key]["unit"],
                "ci_95": f"{ci_lower:.2f} – {ci_upper:.2f}",
            }
        return results

    def estimate_confidence_interval(
        self, value: float, rel_error: float = 0.1
    ) -> Tuple[float, float]:
        """Approximate ±10% confidence interval if uncertainty isn't known"""
        delta = value * rel_error
        return value - delta, value + delta
