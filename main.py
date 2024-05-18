from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from fastapi.middleware.cors import CORSMiddleware
import decimal

app = FastAPI()

DATABASE_URL = "dbname=inventory_wxrq user=inventory_wxrq_user password=32T4vxi3Pe4E703IDoJFRLjLDPnVjaQ6 host=dpg-co2n9f021fec73b0s4g0-a.oregon-postgres.render.com port=5432"

# Allow CORS for all origins during development (replace "*" with your actual frontend URL in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Pydantic models
class Alert(BaseModel):
    location_long: float
    location_lat: float
    source: str

class Location(BaseModel):
    lat: float
    lon: float

class MedicineAlert(BaseModel):
    time: decimal.Decimal  # Use decimal.Decimal for precise numeric handling
    medicine_name: str

# Global variable to store the current location
current_location = Location(lat=0.0, lon=0.0)

@app.get("/alert-history")
async def get_alert_history():
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT * FROM alert_history")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        alert_history = []
        for row in rows:
            serial_number, time_stamp, location_long, location_lat, source = row
            alert_history.append({
                "serial_number": serial_number,
                "time_stamp": time_stamp,
                "location_long": location_long,
                "location_lat": location_lat,
                "source": source
            })

        return alert_history

    except (Exception, psycopg2.Error) as error:
        return {"status": "error", "detail": str(error)}

    finally:
        if conn:
            conn.close()

@app.post("/insert-alert")
async def insert_alert(alert: Alert):
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        sql = "INSERT INTO alert_history (time_stamp, location_long, location_lat, source) VALUES (%s, %s, %s, %s) RETURNING serial_number"
        current_time = datetime.now()
        cur.execute(sql, (current_time, alert.location_long, alert.location_lat, alert.source))
        serial_number = cur.fetchone()[0]
        conn.commit()
        cur.close()

        return {"status": "success", "serial_number": serial_number, "message": "Alert inserted successfully"}

    except (Exception, psycopg2.Error) as error:
        return {"status": "error", "detail": str(error)}

    finally:
        if conn:
            conn.close()

@app.post("/update-location")
async def update_location(location: Location):
    global current_location
    current_location = location
    return {"status": "success", "message": "Location updated successfully"}

@app.get("/get-location")
async def get_location():
    return current_location

@app.get("/medicine-alert")
async def get_medicine_alert():
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute('SELECT "time", "medicine_name" FROM "Medicine_Alert"')
        rows = cur.fetchall()
        cur.close()
        conn.close()

        medicine_alerts = [{"time": str(row[0]), "medicine_name": row[1]} for row in rows]

        return medicine_alerts

    except (Exception, psycopg2.Error) as error:
        return {"status": "error", "detail": str(error)}

    finally:
        if conn:
            conn.close()

@app.post("/medicine-reminder")
async def update_medicine_alert(medicine_alert: MedicineAlert):
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        sql = 'UPDATE "Medicine_Alert" SET "time" = %s, "medicine_name" = %s WHERE "id" = 1 RETURNING id'
        cur.execute(sql, (medicine_alert.time, medicine_alert.medicine_name))
        id = cur.fetchone()[0]
        conn.commit()
        cur.close()

        return {"status": "success", "id": id, "message": "Medicine alert updated successfully"}

    except (Exception, psycopg2.Error) as error:
        return {"status": "error", "detail": str(error)}

    finally:
        if conn:
            conn.close()
