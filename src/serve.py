from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
try:
    from google.cloud import storage
except ImportError:
    storage = None
import joblib
import os

app = FastAPI()

ARTIFACT_BUCKET = os.environ.get("ARTIFACT_BUCKET", "income-lab-bucket")
MODEL_KEY = "artifacts/current/model.joblib"
MODEL_PATH = os.path.expanduser("~/models/model.joblib")


def download_model():
    """
    Tai file model.joblib tu cloud storage ve may khi server khoi dong.

    Ham nay duoc goi mot lan khi module duoc import. Su dung
    GOOGLE_APPLICATION_CREDENTIALS de xac thuc (duoc dat trong systemd service).
    """
    try:
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        if storage is not None:
            client = storage.Client()
            bucket = client.bucket(ARTIFACT_BUCKET)
            blob = bucket.blob(MODEL_KEY)
            blob.download_to_filename(MODEL_PATH)
            print("Model da duoc tai xuong tu cloud storage.")
        else:
            raise RuntimeError("google-cloud-storage not installed")
    except Exception as e:
        print(f"Warning: Could not download model from cloud storage: {e}")
        if not os.path.exists(MODEL_PATH) and os.path.exists("models/model.joblib"):
            import shutil
            shutil.copy("models/model.joblib", MODEL_PATH)
            print("Loaded local fallback model.")


download_model()
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
elif os.path.exists("models/model.joblib"):
    model = joblib.load("models/model.joblib")
else:
    model = None


class ScoreRequest(BaseModel):
    features: list[float]


@app.get("/healthz")
def healthz():
    """
    Endpoint kiem tra suc khoe server.
    GitHub Actions goi endpoint nay sau khi deploy de xac nhan server dang chay.

    Tra ve: {"status": "ok"}
    """
    return {"status": "ok"}


@app.post("/score")
def score(req: ScoreRequest):
    """
    Endpoint suy luan chinh.

    Dau vao : JSON {"features": [f1, f2, ..., f10]}
    Dau ra  : JSON {"prediction": <0|1>, "label": <"thu_nhap_thap"|"thu_nhap_cao">}

    Thu tu 10 dac trung (khop voi thu tu trong FEATURE_NAMES cua test):
        age, workclass, education_num, marital_status, occupation,
        relationship, sex, capital_gain, capital_loss, hours_per_week
    """
    # 6: Kiem tra so luong dac trung
    if len(req.features) != 10:
        raise HTTPException(status_code=400, detail="Expected 10 features (adult income)")

    if model is None:
        raise HTTPException(status_code=503, detail="Model is not loaded")

    # 7: Goi model.predict([req.features]) de lay ket qua du doan
    pred = int(model.predict([req.features])[0])

    # 8: Tra ve dict chua prediction (int) va label (string)
    label = "thu_nhap_cao" if pred == 1 else "thu_nhap_thap"
    return {"prediction": pred, "label": label}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
