import os
import math
import numpy as np
import xgboost as xgb
from typing import Dict, Tuple
from app.schemas.predict import PredictInput


class PredictService:
    def __init__(self):
        # Registry of models with filenames and display metadata
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

        # Thresholds to decide which value is "better" (original vs. log-back-transformed)
        # Rule below: if original prediction < threshold → pick lg-*; otherwise pick original
        self.opt_thresholds: Dict[str, float] = {
            "growing-stock": 206.0,
            "trunk": 93.5,
            "trunk-bark": 9.3,
            "branch": 10.82,
            "foliage": 4.3,
        }

        # Pairs of base model keys ↔ their log-back-transformed counterparts
        self.model_pairs: Dict[str, str] = {
            "growing-stock": "lg-growing-stock",
            "trunk": "lg-trunk",
            "trunk-bark": "lg-trunk-bark",
            "branch": "lg-branch",
            "foliage": "lg-foliage",
        }

        self.models = self.load_models()

    def load_models(self) -> Dict[str, xgb.XGBRegressor]:
        """
        Load all XGBoost models from disk into memory.

        Returns
        -------
        Dict[str, xgb.XGBRegressor]
            Mapping from model key to a loaded XGBRegressor.
        """
        # Relative or absolute directory containing the saved model files
        model_dir = "models/xgboost-models/tree-biomass"

        models: Dict[str, xgb.XGBRegressor] = {}
        for key, info in self.model_info.items():
            path = os.path.join(model_dir, info["file"])
            model = xgb.XGBRegressor()
            # Model file must match how it was saved (e.g., via model.save_model(path))
            model.load_model(path)
            models[key] = model
        return models

    def predict(self, data: PredictInput) -> Dict[str, Dict[str, Dict[str, str]]]:
        """
        Run all models, produce two dictionaries:
          - 'all_results': every model's prediction and metadata
          - 'optimum_values': per base metric, choose between base and lg-* using thresholds

        Returns
        -------
        Dict[str, Dict[str, Dict[str, str]]]
            {
              "all_results": { "<key>": {"label":..., "value":..., "unit":..., "ci_95":...}, ... },
              "optimum_values": { "<base_key>": {...chosen payload...}, ... }
            }
        """
        # Build feature vector in the expected order/types
        features = np.array(
            [[int(data.sp), int(data.origin), data.h, data.dbh, data.ba]]
        )

        all_results: Dict[str, Dict[str, str]] = (
            {}
        )  # pretty payloads (strings) for every model
        raw_values: Dict[str, float] = {}  # numeric values for decision logic

        # 1) Run every model and collect results
        for key, model in self.models.items():
            yhat = float(model.predict(features)[0])

            # Back-transform if the model was trained on log(y)
            if key.startswith("lg-"):
                yhat = math.exp(yhat)

            ci_lower, ci_upper = self.estimate_confidence_interval(yhat)

            payload = {
                "label": self.model_info[key]["label"],
                "value": f"{yhat:.0f}",  # format as integer-like string; change to .2f if needed
                "unit": self.model_info[key]["unit"],
                "ci_95": f"{ci_lower:.0f} – {ci_upper:.0f}",
            }

            all_results[key] = payload
            raw_values[key] = yhat

        # 2) Build 'optimum_values' using thresholds and the base (non-lg) predictions
        optimum_values: Dict[str, Dict[str, str]] = {}
        for base_key, lg_key in self.model_pairs.items():
            threshold = self.opt_thresholds[base_key]

            base_val = raw_values.get(base_key)
            lg_val = raw_values.get(lg_key)

            # If either value is missing, skip this metric gracefully
            if base_val is None or lg_val is None:
                continue

            # Decision rule: if original < threshold → choose lg-*; else choose original
            chosen_key = lg_key if base_val < threshold else base_key

            # Store under the base key; payload shape matches 'all_results'
            optimum_values[base_key] = all_results[chosen_key]

        return {
            "all_results": all_results,
            "optimum_values": optimum_values,
        }

    def estimate_confidence_interval(
        self, value: float, rel_error: float = 0.1
    ) -> Tuple[float, float]:
        """
        Rough 95% CI via ±relative error (default ±10%).
        Replace with a proper uncertainty model if available.
        """
        delta = value * rel_error
        return value - delta, value + delta
