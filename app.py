from fastapi import FastAPI, UploadFile, File
import lightgbm as lgb
import numpy as np
import os

# ✅ FIXED import (based on your folder structure)
from thrember.features import PEFeatureExtractor
app = FastAPI(title="Malware Detection API - Phase I")

# ✅ Load model and extractor safely
MODEL_PATH = "best.model"

try:
    print("🚀 Starting app...")
    print("📦 Loading model...")
    model = lgb.Booster(model_file=MODEL_PATH)
    print("✅ Model loaded")

    print("🔧 Initializing extractor...")
    extractor = PEFeatureExtractor()
    print("✅ Extractor ready")

except Exception as e:
    print("❌ Startup failed:", e)
    raise e


@app.get("/")
def home():
    return {"message": "Malware Detection API running 🚀"}


@app.post("/scan")
async def scan_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()

        features = np.array(
            extractor.feature_vector(contents),
            dtype=np.float32
        )

        probability = float(model.predict([features])[0])

        if probability >= 0.70:
            verdict = "MALICIOUS"
        elif probability <= 0.25:
            verdict = "BENIGN"
        else:
            verdict = "SUSPICIOUS"

        return {
            "filename": file.filename,
            "malware_probability": f"{probability * 100:.2f}%",
            "verdict": verdict,
            "status": "success"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


# ✅ Local run only (Render ignores this)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)