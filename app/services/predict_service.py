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
            "branch": {
                "file": "04_M_branch.json",
                "unit": "t/ha",
                "label": "Branch biomass",
            },
            "foliage": {
                "file": "05_M_foliage.json",
                "unit": "t/ha",
                "label": "Foliage biomass",
            },
            "lg-growing-stock": {
                "file": "01_LN_GS.json",
                "unit": "m³/ha",
                "label": "Growing stock generated on the log scale and back-transformed to the original scale",
            },
            "lg-trunk": {
                "file": "02_LN_M_all_stem.json",
                "unit": "t/ha",
                "label": "Total trunk biomass generated on the log scale and back-transformed to the original scale",
            },
            "lg-trunk-bark": {
                "file": "03_LN_M_stem_bark.json",
                "unit": "t/ha",
                "label": "Trunk bark biomass generated on the log scale and back-transformed to the original scale",
            },
            "lg-branch": {
                "file": "04_LN_M_branch.json",
                "unit": "t/ha",
                "label": "Branch biomass generated on the log scale and back-transformed to the original scale",
            },
            "lg-foliage": {
                "file": "05_LN_M_foliage.json",
                "unit": "t/ha",
                "label": "Foliage biomass generated on the log scale and back-transformed to the original scale",
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
            print(f"Model: {key}, Prediction: {prediction}")
            output = float(prediction[0])
            if "lg-" in key:
                output = np.exp(output)  # зворотне перетворення логарифму
            ci_lower, ci_upper = self.estimate_confidence_interval(output)
            results.all[key] = {
                "label": self.model_info[key]["label"],
                "value": f"{output:.0f}",
                "unit": self.model_info[key]["unit"],
                "ci_95": f"{ci_lower:.0f} – {ci_upper:.0f}",
            }
        return results

    def estimate_confidence_interval(
        self, value: float, rel_error: float = 0.1
    ) -> Tuple[float, float]:
        """Approximate ±10% confidence interval if uncertainty isn't known"""
        delta = value * rel_error
        return value - delta, value + delta
