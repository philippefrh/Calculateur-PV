from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models for Solar Calculator
class ClientInfo(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    # Personal Info
    first_name: str
    last_name: str
    address: str
    
    # Technical Info
    roof_surface: float
    roof_orientation: str
    velux_count: int
    
    # Heating System
    heating_system: str
    
    # Water Heating
    water_heating_system: str
    water_heating_capacity: Optional[int] = None
    
    # Consumption
    annual_consumption_kwh: float
    monthly_edf_payment: float
    annual_edf_payment: float
    
    # Calculation Results
    recommended_kit_power: Optional[int] = None
    estimated_production: Optional[float] = None
    estimated_savings: Optional[float] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ClientInfoCreate(BaseModel):
    first_name: str
    last_name: str
    address: str
    roof_surface: float
    roof_orientation: str
    velux_count: int
    heating_system: str
    water_heating_system: str
    water_heating_capacity: Optional[int] = None
    annual_consumption_kwh: float
    monthly_edf_payment: float
    annual_edf_payment: float

class SolarCalculation(BaseModel):
    client_id: str
    kit_power: int
    panel_count: int
    estimated_production: float
    estimated_savings: float
    autonomy_percentage: float
    monthly_savings: float
    financing_options: List[dict]

# Solar Kit Pricing
SOLAR_KITS = {
    3: {"price": 14900, "panels": 6},
    4: {"price": 20900, "panels": 8},
    5: {"price": 21900, "panels": 10},
    6: {"price": 22900, "panels": 12},
    7: {"price": 24900, "panels": 14},
    8: {"price": 26900, "panels": 16},
    9: {"price": 29900, "panels": 18}
}

# Routes
@api_router.get("/")
async def root():
    return {"message": "Solar Calculator API"}

@api_router.post("/clients", response_model=ClientInfo)
async def create_client(client_data: ClientInfoCreate):
    try:
        client_dict = client_data.dict()
        client_obj = ClientInfo(**client_dict)
        await db.clients.insert_one(client_obj.dict())
        return client_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/clients", response_model=List[ClientInfo])
async def get_clients():
    try:
        clients = await db.clients.find().to_list(1000)
        return [ClientInfo(**client) for client in clients]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/clients/{client_id}", response_model=ClientInfo)
async def get_client(client_id: str):
    try:
        client = await db.clients.find_one({"id": client_id})
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        return ClientInfo(**client)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/calculate/{client_id}")
async def calculate_solar_solution(client_id: str):
    try:
        client = await db.clients.find_one({"id": client_id})
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Simple calculation logic (to be enhanced later)
        annual_consumption = client['annual_consumption_kwh']
        
        # Find best kit size
        best_kit = 3
        for kit_power in SOLAR_KITS.keys():
            if kit_power * 1000 <= annual_consumption * 1.2:  # 20% buffer
                best_kit = kit_power
        
        kit_info = SOLAR_KITS[best_kit]
        
        # Mock calculations (to be replaced with real formulas)
        estimated_production = best_kit * 1200  # ~1200 kWh per kW
        autonomy_percentage = min(95, (estimated_production / annual_consumption) * 100)
        annual_savings = estimated_production * 0.2516  # Current EDF rate
        monthly_savings = annual_savings / 12
        
        calculation = SolarCalculation(
            client_id=client_id,
            kit_power=best_kit,
            panel_count=kit_info['panels'],
            estimated_production=estimated_production,
            estimated_savings=annual_savings,
            autonomy_percentage=autonomy_percentage,
            monthly_savings=monthly_savings,
            financing_options=[
                {"duration": 120, "monthly_payment": kit_info['price'] / 120},
                {"duration": 180, "monthly_payment": kit_info['price'] / 180}
            ]
        )
        
        return calculation
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/solar-kits")
async def get_solar_kits():
    return SOLAR_KITS

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()