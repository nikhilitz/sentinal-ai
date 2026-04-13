from fastapi import FastAPI, UploadFile, File
import lightgbm as lgb
import numpy as np
import os

from thrember.features import PEFeatureExtractor

app = FastAPI(title="Malware Detection API - Phase I")

# Global variables
model = None
extractor = None

# ✅ Safe startup loading
@app.on_event("startup")
def load_model():
    global model, extractor
    try:
        print("🚀 Starting app...")

        print("📦 Loading model...")
        model = lgb.Booster(model_file="best.model")
        print("✅ Model loaded")

        print("🔧 Initializing extractor...")
        extractor = PEFeatureExtractor()
        print("✅ Extractor ready")

    except Exception as e:
        print("❌ Startup failed:", e)


# ✅ Health check route
@app.get("/")
def home():
    return {"message": "Malware Detection API running 🚀"}


# ✅ Scan endpoint
@app.post("/scan")
async def scan_file(file: UploadFile = File(...)):
    try:
        if model is None or extractor is None:
            return {
                "status": "error",
                "message": "Model not loaded properly"
            }

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


# ✅ Local run (ignored in deployment)
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)