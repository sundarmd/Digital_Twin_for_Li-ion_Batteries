from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np
from Digital_Twin_for_Li-ion_Batteries.config import MODEL_PATH_RF

app = FastAPI()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@app.get("/battery/{battery_id}")
def get_battery_data(battery_id: int):
    db = SessionLocal()
    try:
        battery_data = db.query(BatteryData).filter(BatteryData.id == battery_id).first()
        if battery_data is None:
            raise HTTPException(status_code=404, detail="Battery data not found")
        return {
            "id": battery_data.id,
            "timestamp": battery_data.timestamp,
            "voltage": battery_data.voltage,
            "current": battery_data.current,
            "temperature": battery_data.temperature,
            "state_of_charge": battery_data.state_of_charge,
            "capacity": battery_data.capacity
        }
    finally:
        db.close()

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)