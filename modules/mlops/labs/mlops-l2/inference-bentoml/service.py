import logging
import os

import bentoml
import mlflow
import pandas as pd
from pydantic import BaseModel

# -------------------- Constants --------------------
ARTIFACT_MODEL_NAME = "model"
MLFLOW_TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI", "http://mlflow:5000")

# -------------------- Logging --------------------
logger = logging.getLogger("spaceflight_service")
logger.setLevel(logging.INFO)

# -------------------- Pydantic Models --------------------
class SpaceflightInput(BaseModel):
    engines: float
    passenger_capacity: int
    crew: float
    d_check_complete: bool
    moon_clearance_complete: bool
    iata_approved: bool
    company_rating: float
    review_scores_rating: float

class ModelURI(BaseModel):
    model_name: str
    model_version: int

# -------------------- BentoML Service --------------------
@bentoml.service(name="spaceflight_service")
class SpaceflightService:
    def __init__(self):
        self.bento_model = None
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

    # -------------------- Model Import Endpoint --------------------
    @bentoml.api(route="/import_model")
    async def import_model(self, model_uri: ModelURI) -> dict:
        """
        Imports and loads a model from MLflow into BentoML.
        """
        try:
            await self._load_model(model_uri)
            msg = f"Model {model_uri.model_name}/{model_uri.model_version} is imported and loaded."
            logger.info(msg)
            return {"message": msg}
        except Exception as e:
            logger.exception(f"Error importing model: {e}")
            return {"error": str(e)}

    async def _load_model(self, model_uri: ModelURI) -> None:
        """
        Helper function to import and load MLflow model into BentoML.
        """
        imported_model = bentoml.mlflow.import_model(
            name=model_uri.model_name,
            model_uri=f"models:/{model_uri.model_name}/{model_uri.model_version}"
        )
        self.bento_model = bentoml.mlflow.load_model(imported_model)

    # -------------------- Prediction Endpoint --------------------
    @bentoml.api(route="/predict")
    def predict(self, input_data: SpaceflightInput) -> dict:
        """
        Makes a prediction using the loaded BentoML model.
        """
        if self.bento_model is None:
            msg = "No model loaded. Please import a model first."
            logger.warning(msg)
            return {"error": msg}

        try:
            df = pd.DataFrame.from_records([input_data.model_dump()])
            prediction = self.bento_model.predict(df)
            return {"prediction": prediction.tolist()}
        except Exception as e:
            logger.exception(f"Prediction error: {e}")
            return {"error": "Prediction failed", "details": str(e)}
