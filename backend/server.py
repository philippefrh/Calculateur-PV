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
app = FastAPI(title="FRH ENVIRONNEMENT - API Solaire")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class SolarQuote(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    # Informations personnelles
    prenom: str
    nom: str
    adresse: str
    # Informations logement
    type_logement: Optional[str] = None
    surface_toiture: Optional[float] = None
    orientation_toiture: Optional[str] = None
    # Consommation électrique
    consommation_annuelle: Optional[float] = None
    facture_mensuelle: Optional[float] = None
    # Contact
    telephone: str
    email: Optional[str] = None
    horaires_contact: Optional[str] = None
    # Calculs
    kit_power: Optional[float] = None
    autonomy: Optional[float] = None
    annual_production: Optional[float] = None
    guaranteed_savings: Optional[float] = None
    total_cost_ttc: Optional[float] = None
    # Métadonnées
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "draft"  # draft, completed, sent

class SolarQuoteCreate(BaseModel):
    prenom: str
    nom: str
    adresse: str
    type_logement: Optional[str] = None
    surface_toiture: Optional[float] = None
    orientation_toiture: Optional[str] = None
    consommation_annuelle: Optional[float] = None
    facture_mensuelle: Optional[float] = None
    telephone: str
    email: Optional[str] = None
    horaires_contact: Optional[str] = None

class PVGISCalculation(BaseModel):
    latitude: float
    longitude: float
    annual_production: float
    monthly_data: List[float]
    optimal_angle: float
    optimal_azimuth: float

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "FRH ENVIRONNEMENT - API Solaire v1.0"}

@api_router.post("/solar-quote", response_model=SolarQuote)
async def create_solar_quote(quote_data: SolarQuoteCreate):
    """Créer un nouveau devis solaire"""
    try:
        # Calculs automatiques basés sur les données
        kit_power = 9.0  # kW par défaut
        autonomy = 95.0  # % par défaut
        annual_production = 10944.0  # kWh par défaut
        guaranteed_savings = 2177.0  # € par défaut
        total_cost_ttc = 29900.0  # € par défaut
        
        # Ajustements basés sur la consommation si fournie
        if quote_data.consommation_annuelle:
            # Calcul adaptatif de la puissance
            kit_power = min(max(quote_data.consommation_annuelle / 1200, 3), 12)
            annual_production = kit_power * 1216  # kWh/kW
            guaranteed_savings = annual_production * 0.2  # Estimation économies
            total_cost_ttc = kit_power * 3322  # Prix par kW
        
        quote_dict = quote_data.dict()
        quote_obj = SolarQuote(
            **quote_dict,
            kit_power=kit_power,
            autonomy=autonomy,
            annual_production=annual_production,
            guaranteed_savings=guaranteed_savings,
            total_cost_ttc=total_cost_ttc,
            status="completed"
        )
        
        # Sauvegarder en base
        await db.solar_quotes.insert_one(quote_obj.dict())
        
        return quote_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création du devis: {str(e)}")

@api_router.get("/solar-quotes", response_model=List[SolarQuote])
async def get_solar_quotes():
    """Récupérer tous les devis solaires"""
    try:
        quotes = await db.solar_quotes.find().to_list(1000)
        return [SolarQuote(**quote) for quote in quotes]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des devis: {str(e)}")

@api_router.get("/solar-quote/{quote_id}", response_model=SolarQuote)
async def get_solar_quote(quote_id: str):
    """Récupérer un devis solaire par ID"""
    try:
        quote = await db.solar_quotes.find_one({"id": quote_id})
        if not quote:
            raise HTTPException(status_code=404, detail="Devis non trouvé")
        return SolarQuote(**quote)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération du devis: {str(e)}")

@api_router.post("/pvgis-calculation")
async def calculate_pvgis(address: str):
    """Calculer la production solaire via PVGIS pour une adresse donnée"""
    try:
        # Simulation de calcul PVGIS (à remplacer par vraie intégration)
        calculation = PVGISCalculation(
            latitude=43.6047,  # Exemple Cannes
            longitude=7.0657,
            annual_production=10944.0,
            monthly_data=[450, 620, 890, 1150, 1320, 1420, 1380, 1250, 950, 680, 480, 390],
            optimal_angle=30.0,
            optimal_azimuth=180.0
        )
        return calculation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur calcul PVGIS: {str(e)}")

@api_router.get("/financing-options/{kit_power}")
async def get_financing_options(kit_power: float):
    """Calculer les options de financement pour une puissance donnée"""
    try:
        base_cost = kit_power * 3322  # Prix de base par kW
        
        options = []
        for duration in range(6, 16):
            monthly_payment = base_cost / (duration * 12) * 1.05  # Avec intérêts
            monthly_savings = kit_power * 20  # Estimation économies mensuelles
            difference = monthly_savings - monthly_payment
            
            options.append({
                "duration": duration,
                "monthly_payment": round(monthly_payment),
                "monthly_savings": round(monthly_savings),
                "difference": round(difference)
            })
        
        return {"options": options, "base_cost": base_cost}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur calcul financement: {str(e)}")

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
