from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import psycopg2
import os
from datetime import datetime, timedelta

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class BatteryStatus(BaseModel):
    battery_id: str
    voltage: float
    current: float
    temperature: float
    capacity: float
    timestamp: datetime

def get_db_connection():
    return psycopg2.connect(os.environ['DATABASE_URL'])

@app.get("/battery/{battery_id}/status")
async def get_battery_status(battery_id: str, token: str = Depends(oauth2_scheme)):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT voltage, current, temperature, capacity, timestamp
            FROM battery_data
            WHERE battery_id = %s
            ORDER BY timestamp DESC
            LIMIT 1
        """, (battery_id,))
        result = cur.fetchone()
        cur.close()

        if result is None:
            raise HTTPException(status_code=404, detail="Battery not found")

        return BatteryStatus(
            battery_id=battery_id,
            voltage=result[0],
            current=result[1],
            temperature=result[2],
            capacity=result[3],
            timestamp=result[4]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

@app.get("/battery/{battery_id}/history")
async def get_battery_history(battery_id: str, days: int = 7, token: str = Depends(oauth2_scheme)):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT voltage, current, temperature, capacity, timestamp
            FROM battery_data
            WHERE battery_id = %s AND timestamp > %s
            ORDER BY timestamp ASC
        """, (battery_id, datetime.now() - timedelta(days=days)))
        results = cur.fetchall()
        cur.close()

        if not results:
            raise HTTPException(status_code=404, detail="No data found for the specified battery and time range")

        return [
            BatteryStatus(
                battery_id=battery_id,
                voltage=row[0],
                current=row[1],
                temperature=row[2],
                capacity=row[3],
                timestamp=row[4]
            )
            for row in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)