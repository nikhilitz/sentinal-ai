from fastapi import FastAPI, UploadFile, File
import lightgbm as lgb
import thrember
import numpy as np
import uvicorn

app = FastAPI(title="Malware Detection API - Phase I")

# Load your custom model and extractor globally for speed
MODEL_PATH = "best.model"
model = lgb.Booster(model_file=MODEL_PATH)
extractor = thrember.PEFeatureExtractor()
@app.get("/")
def home():
    return {"message": "Malware Detection API running "}

@app.post("/scan")
async def scan_file(file: UploadFile = File(...)):
    try:
        # Read the uploaded file bytes
        contents = await file.read()
        
        # Extract features (2568-dimensional)
        features = np.array(extractor.feature_vector(contents), dtype=np.float32)
        
        # Predict
        probability = float(model.predict([features])[0])
        
        # Determine Verdict
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
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    # This runs the server on your local IP
    uvicorn.run(app, host="0.0.0.0", port=8000)