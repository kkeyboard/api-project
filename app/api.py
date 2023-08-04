from fastapi import FastAPI, Request
from functools import wraps
from datetime import datetime

from http import HTTPStatus
from typing import Dict

from pathlib import Path
# from config import logger
# from tagifai import main

# Define application
app = FastAPI(
    title="api-projects-01",
    description="Using FastAPI and uvicorn ASGI server to create API services",
    version="0.1"
)

def construct_response(f):
    # Construct a JSON response for an endpoint. 
    @wraps(f)
    def wrap(request: Request, *args, **kwargs) -> Dict:
        results = f(request, *args, **kwargs)
        response = {
            "message": results["message"],
            "method": request.method,
            "status-code": results["status-code"],
            "timestamp": datetime.now().isoformat(),
            "url": request.url._url,
        }
        if "data" in results:
            response["data"] = results["data"]
        return response
    
    return wrap

@app.get("/", tags=["General"])
@construct_response
def _index(request: Request) -> Dict:
    # Health check. 
    response = {
        "message": HTTPStatus.OK.phrase,
        "status-code": HTTPStatus.OK,
        "data": {},
    }
    return response

# When "startup" event happens, it loads the artifacts for the model to use inference. 
# @app.on_event("startup")
# def load_artifacts():
#     global artifacts
#     run_id = open(Path(config.CONFIG_DIR, "run_id.txt")).read()
#     artifacts = main.load_artifacts(model_dir=config.MODEL_DIR)
#     logger.info("Ready for inference")