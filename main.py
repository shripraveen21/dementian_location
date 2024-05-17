from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

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

# Endpoint to get alert history
@app.get("/alert-history")
async def get_alert_history():
    conn = None
    try:
        # Connect to the PostgreSQL DB
        conn = psycopg2.connect(DATABASE_URL)

        # Open a cursor to perform DB operations
        cur = conn.cursor()

        # Execute the query to fetch all rows from alert_history table
        cur.execute("SELECT * FROM alert_history")

        # Fetch all rows
        rows = cur.fetchall()

        # Close communication with the DB
        cur.close()
        conn.close()

        # Convert the rows to a list of dictionaries
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
        # Close communication with the DB
        if conn:
            conn.close()

# Endpoint to insert alert data
@app.post("/insert-alert")
async def insert_alert(alert: Alert):
    conn = None
    try:
        # Connect to the PostgreSQL DB
        conn = psycopg2.connect(DATABASE_URL)

        # Open a cursor to perform DB operations
        cur = conn.cursor()

        # Construct the SQL query to insert data into the table
        sql = "INSERT INTO alert_history (time_stamp, location_long, location_lat, source) VALUES (%s, %s, %s, %s) RETURNING serial_number"

        # Get the current timestamp
        current_time = datetime.now()

        # Execute the SQL query
        cur.execute(sql, (current_time, alert.location_long, alert.location_lat, alert.source))

        # Fetch the serial number of the inserted row
        serial_number = cur.fetchone()[0]

        # Commit the transaction
        conn.commit()

        # Close communication with the DB
        cur.close()

        return {"status": "success", "serial_number": serial_number, "message": "Alert inserted successfully"}

    except (Exception, psycopg2.Error) as error:
        return {"status": "error", "detail": str(error)}

    finally:
        # Close communication with the DB
        if conn:
            conn.close()
          
# New Endpoint to get the current location# Pydantic model for location
class Location(BaseModel):
    lat: float
    lon: float
# Global variable to store the current location
current_location = Location(lat=0.0, lon=0.0)

@app.post("/update-location")
async def update_location(location: Location):
    global current_location
    current_location = location
    return {"status": "success", "message": "Location updated successfully"}

@app.get("/get-location")
async def get_location():
    return current_location
