from fastapi import FastAPI, APIRouter, HTTPException, Response
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import requests
import aiohttp
import asyncio
from geopy.geocoders import Nominatim
import json
import io
import base64
from io import BytesIO
from PIL import Image as PILImage, ImageDraw

# PDF Generation imports
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.lib.utils import ImageReader
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import requests

# OpenAI Vision imports - Updated LLMChat to LlmChat
from emergentintegrations.llm.chat import ImageContent, UserMessage, LlmChat

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

# PVGIS Configuration
PVGIS_BASE_URL = "https://re.jrc.ec.europa.eu/api/v5_2"

# Configuration des modes de calcul
CALCULATION_MODES = {
    "realistic": {
        "name": "Etude 1",
        "description": "Calculs basés sur les standards du marché",
        "autoconsumption_rate": 0.85,  # 85% autoconsommation (plus réaliste)
        "optimization_coefficient": 1.0,  # Pas d'optimisation comportementale
        "maintenance_savings": 100,  # €/year (réduction maintenance réseau)
        "annual_rate_increase": 0.03,  # 3% augmentation EDF par an
        "surplus_sale_rate": 0.076,  # €/kWh pour surplus vendu à EDF
        "autonomy_cap": 100  # Pas de plafond artificiel
    },
    "optimistic": {
        "name": "Etude 2",
        "description": "Calculs optimisés pour objectifs commerciaux",
        "autoconsumption_rate": 0.98,  # 98% autoconsommation (très optimiste)
        "optimization_coefficient": 1.24,  # +24% d'économies comportementales
        "maintenance_savings": 300,  # €/year (économies maintenance importantes)
        "annual_rate_increase": 0.05,  # 5% augmentation EDF par an
        "surplus_sale_rate": 0.076,  # €/kWh pour surplus vendu à EDF
        "autonomy_cap": 95  # Plafond à 95% pour l'affichage
    }
}

# Configuration des régions
REGIONS_CONFIG = {
    "france": {
        "name": "France",
        "logo_subtitle": None,
        "company_info": {
            "name": "FRH ENVIRONNEMENT",
            "address": "Adresse France (actuelle)",  # À mettre à jour avec la vraie adresse
            "phone": "09 85 60 50 51",
            "email": "direction@francerenovhabitat.com",
            "tva": "FR52890493737",
            "subtitle": "FRH ENVIRONNEMENT - Énergie Solaire Professionnel"
        },
        "interest_rates": {
            "standard": 0.0496,  # 4.96% TAEG
            "with_aids": 0.0496  # 4.96% TAEG
        },
        "kits": {
            # Configuration actuelle France - à récupérer depuis la base
        },
        "financing": {
            "min_duration": 5,
            "max_duration": 15,
            "aids_recovery_months": 7  # Récupération entre 7-12 mois
        }
    },
    "martinique": {
        "name": "Martinique",
        "logo_subtitle": "Région Martinique",
        "company_info": {
            "name": "FRH MARTINIQUE",
            "address": "11 rue des Arts et Métiers\n97200 Fort-de-France",
            "phone": "09 85 60 50 51",
            "email": "direction@francerenovhabitat.com",
            "tva": "FR52890493737",
            "subtitle": "FRH ENVIRONNEMENT - Énergie Solaire Professionnel"
        },
        "interest_rates": {
            "standard": 0.0863,  # 8.63% TAEG
            "with_aids": 0.0863  # 8.63% TAEG
        },
        "kits": {
            "kit_3kw": {
                "power": 3,
                "price_ttc": 10900,
                "aid_amount": 5340,
                "surface": 15,  # m² estimée
                "description": "Kit 3kW - Résidentiel"
            },
            "kit_6kw": {
                "power": 6,
                "price_ttc": 15900,
                "aid_amount": 6480,
                "surface": 30,  # m² estimée
                "description": "Kit 6kW - Résidentiel+"
            },
            "kit_9kw": {
                "power": 9,
                "price_ttc": 18900,
                "aid_amount": 9720,
                "surface": 45,  # m² estimée
                "description": "Kit 9kW - Grande résidence"
            },
            "kit_12kw": {
                "power": 12,
                "price_ttc": 22900,
                "aid_amount": 9720,
                "surface": 60,  # m² estimée
                "description": "Kit 12kW - Résidentiel large"
            },
            "kit_15kw": {
                "power": 15,
                "price_ttc": 25900,
                "aid_amount": 12150,
                "surface": 75,  # m² estimée
                "description": "Kit 15kW - Commercial petit"
            },
            "kit_18kw": {
                "power": 18,
                "price_ttc": 28900,
                "aid_amount": 14580,
                "surface": 90,  # m² estimée
                "description": "Kit 18kW - Commercial moyen"
            },
            "kit_21kw": {
                "power": 21,
                "price_ttc": 30900,
                "aid_amount": 17010,
                "surface": 105,  # m² estimée
                "description": "Kit 21kW - Commercial+"
            },
            "kit_24kw": {
                "power": 24,
                "price_ttc": 32900,
                "aid_amount": 19440,
                "surface": 120,  # m² estimée
                "description": "Kit 24kW - Commercial large"
            },
            "kit_27kw": {
                "power": 27,
                "price_ttc": 34900,
                "aid_amount": 21870,
                "surface": 135,  # m² estimée
                "description": "Kit 27kW - Commercial XL"
            }
        },
        "financing": {
            "min_duration": 3,
            "max_duration": 15,
            "aids_recovery_months": 3  # Récupération 3-4 mois après installation
        }
    }
}

# Define Models for Solar Calculator
class ClientInfo(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    # Personal Info
    first_name: str
    last_name: str
    address: str
    phone: Optional[str] = None
    email: Optional[str] = None
    
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
    
    # Location data from geocoding
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Calculation Results
    recommended_kit_power: Optional[int] = None
    estimated_production: Optional[float] = None
    estimated_savings: Optional[float] = None
    pvgis_data: Optional[Dict[str, Any]] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ClientInfoCreate(BaseModel):
    first_name: str
    last_name: str
    address: str
    phone: str
    email: str
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
    pvgis_annual_production: Optional[float] = None
    pvgis_monthly_data: Optional[List[dict]] = None

class PVGISData(BaseModel):
    latitude: float
    longitude: float
    annual_production: float
    monthly_data: List[dict]
    orientation_factor: float

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

# EDF rates and constants
EDF_RATE_PER_KWH = 0.2516  # €/kWh
ANNUAL_RATE_INCREASE = 0.05  # 5% per year
SURPLUS_SALE_RATE = 0.076  # €/kWh for surplus sold to EDF
AUTOCONSUMPTION_AID = 80  # €/kW installed
TVA_RATE = 0.20  # 20% TVA (except 3kW)

# Orientation factors for PVGIS
ORIENTATION_ASPECTS = {
    "Sud": 0,
    "Sud-Est": -45,
    "Sud-Ouest": 45,
    "Est": -90,
    "Ouest": 90
}

def detect_region_from_address(address: str) -> str:
    """
    Detect region (france or martinique) from address string
    """
    address_lower = address.lower()
    if any(keyword in address_lower for keyword in ["martinique", "97200", "97201", "97202", "97203", "97204", "97205", "fort-de-france", "schoelcher", "lamentin"]):
        return "martinique"
    return "france"

async def geocode_address(address: str, region: str = "france") -> tuple[float, float]:
    """
    Convert address to latitude/longitude using geopy
    Falls back to default coordinates if geocoding fails
    """
    # Default coordinates by region
    default_coords = {
        "france": (46.2276, 2.2137),  # Center of France
        "martinique": (14.6415, -61.0242)  # Center of Martinique
    }
    
    try:
        geolocator = Nominatim(user_agent="solar_calculator", timeout=5)
        full_address = f"{address}, {region.title()}" if region == "france" else f"{address}, Martinique"
        location = geolocator.geocode(full_address)
        
        if location:
            logging.info(f"Successfully geocoded address: {address} -> ({location.latitude}, {location.longitude})")
            return location.latitude, location.longitude
        else:
            logging.warning(f"Could not geocode address: {address}, using default coordinates for {region}")
            return default_coords.get(region, default_coords["france"])
    except Exception as e:
        logging.error(f"Geocoding error: {e}")
        logging.warning(f"Using default coordinates for {region}")
        return default_coords.get(region, default_coords["france"])

async def get_pvgis_data(lat: float, lon: float, orientation: str, kit_power: int) -> Dict[str, Any]:
    """
    Get solar production data from PVGIS API
    """
    try:
        aspect = ORIENTATION_ASPECTS.get(orientation, 0)
        
        # PVGIS API parameters
        params = {
            "lat": lat,
            "lon": lon,
            "peakpower": kit_power,  # kW
            "loss": 14,  # 14% system losses (standard)
            "angle": 35,  # Optimal tilt angle for France
            "aspect": aspect,  # Orientation
            "pvtech": "c-Si",  # Crystalline Silicon
            "mounting": "building",  # Building integrated
            "trackingtype": 0,  # Fixed mounting
            "outputformat": "json",
            "browser": 0
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{PVGIS_BASE_URL}/PVcalc", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract relevant data
                    outputs = data.get("outputs", {})
                    totals = outputs.get("totals", {})
                    monthly = outputs.get("monthly", [])
                    
                    return {
                        "annual_production": totals.get("fixed", {}).get("E_y", 0),  # kWh/year
                        "monthly_data": monthly,
                        "specific_production": totals.get("fixed", {}).get("E_y", 0) / kit_power if kit_power > 0 else 0,  # kWh/kW/year
                        "raw_pvgis_data": data
                    }
                else:
                    raise HTTPException(status_code=500, detail=f"PVGIS API error: {response.status}")
                    
    except Exception as e:
        logging.error(f"PVGIS API error: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching PVGIS data: {str(e)}")

def calculate_optimal_kit_size_martinique(annual_consumption: float, roof_surface: float) -> str:
    """
    Calculate optimal kit size for Martinique based on consumption and roof space
    Returns kit_id (e.g., 'kit_3kw', 'kit_6kw', 'kit_9kw')
    """
    # Each panel is 2.1 m² and 0.5 kW
    max_panels_by_surface = int(roof_surface / 2.1)
    max_power_by_surface = max_panels_by_surface * 0.5
    
    # Target 80-100% of annual consumption
    target_power_by_consumption = annual_consumption / 1400  # Assuming ~1400 kWh/kW/year in Martinique
    
    # Choose the limiting factor
    target_power = min(max_power_by_surface, target_power_by_consumption * 1.1)  # 110% buffer
    
    # Find the closest available kit
    if target_power <= 4:
        return "kit_3kw"
    elif target_power <= 7:
        return "kit_6kw"
    else:
        return "kit_9kw"

def calculate_optimal_kit_size_martinique(annual_consumption: float, roof_surface: float) -> str:
    """
    Calculate optimal kit size for Martinique based on consumption and roof space
    Returns kit_id (e.g., 'kit_3kw', 'kit_6kw', 'kit_9kw')
    """
    # Each panel is 2.1 m² and 0.5 kW
    max_panels_by_surface = int(roof_surface / 2.1)
    max_power_by_surface = max_panels_by_surface * 0.5
    
    # Target 80-100% of annual consumption
    target_power_by_consumption = annual_consumption / 1400  # Assuming ~1400 kWh/kW/year in Martinique
    
    # Choose the limiting factor
    target_power = min(max_power_by_surface, target_power_by_consumption * 1.1)  # 110% buffer
    
    # Find the closest available kit
    if target_power <= 4:
        return "kit_3kw"
    elif target_power <= 7:
        return "kit_6kw"
    else:
        return "kit_9kw"

def calculate_optimal_kit_size(annual_consumption: float, roof_surface: float) -> int:
    """
    Calculate optimal kit size based on consumption and roof space
    """
    # Each panel is 2.1 m² and 0.5 kW
    max_panels_by_surface = int(roof_surface / 2.1)
    max_power_by_surface = max_panels_by_surface * 0.5
    
    # Target 80-100% of annual consumption
    target_power_by_consumption = annual_consumption / 1200  # Assuming ~1200 kWh/kW/year in France
    
    # Choose the limiting factor
    target_power = min(max_power_by_surface, target_power_by_consumption * 1.1)  # 110% buffer
    
    # Find the closest available kit
    available_powers = list(SOLAR_KITS.keys())
    best_power = min(available_powers, key=lambda x: abs(x - target_power))
    
    return best_power

def calculate_financing_options(kit_price: float, monthly_savings: float, region: str = "france") -> List[Dict]:
    """
    Calculate financing options from 3 to 15 years based on region
    """
    region_config = REGIONS_CONFIG.get(region, REGIONS_CONFIG["france"])
    taeg = region_config["interest_rates"]["standard"]
    monthly_rate = taeg / 12
    
    min_duration = region_config["financing"]["min_duration"]
    max_duration = region_config["financing"]["max_duration"]
    
    options = []
    
    for years in range(min_duration, max_duration + 1):
        months = years * 12
        
        if monthly_rate > 0:
            # Standard loan calculation
            monthly_payment = kit_price * (monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)
        else:
            monthly_payment = kit_price / months
        
        # Calculate if it's close to the monthly savings
        savings_ratio = monthly_payment / monthly_savings if monthly_savings > 0 else float('inf')
        
        options.append({
            "duration_years": years,
            "duration_months": months,
            "monthly_payment": round(monthly_payment, 2),
            "savings_ratio": round(savings_ratio, 2),
            "difference_vs_savings": round(monthly_payment - monthly_savings, 2),
            "taeg": taeg
        })
    
    return options

def find_optimal_duration(financing_options: List[Dict], monthly_savings: float) -> int:
    """
    Find the optimal financing duration based on the same logic as frontend
    """
    optimal_option = None
    for option in financing_options:
        if option["difference_vs_savings"] >= -20 and option["difference_vs_savings"] <= 20:
            optimal_option = option
            break
    
    if optimal_option is None:
        optimal_option = financing_options[-1]  # Last option if none found
    
    return optimal_option["duration_years"]

def calculate_financing_with_aids(kit_price: float, total_aids: float, monthly_savings: float, region: str = "france", financing_options: List[Dict] = None) -> Dict:
    """
    Calculate financing options with aids deducted - WITH INTERESTS
    Use mensualité = économie_mensuelle - 25€ for guaranteed positive cash flow
    """
    region_config = REGIONS_CONFIG.get(region, REGIONS_CONFIG["france"])
    taeg = region_config["interest_rates"]["with_aids"]
    monthly_rate = taeg / 12
    
    # Amount to finance after aids
    financed_amount = kit_price - total_aids
    
    # Calculate optimal monthly payment: monthly_savings - 25€ for guaranteed positive cash flow
    target_monthly_payment = monthly_savings - 25
    
    # Ensure minimum payment to avoid unrealistic durations
    min_payment = financed_amount / (15 * 12)  # Maximum 15 years
    max_payment = financed_amount / (3 * 12)   # Minimum 3 years
    
    if target_monthly_payment < min_payment:
        target_monthly_payment = min_payment
    elif target_monthly_payment > max_payment:
        target_monthly_payment = max_payment
    
    # Calculate duration for this monthly payment
    if monthly_rate > 0:
        # Solve for number of months: target_payment = financed_amount * [r * (1+r)^n] / [(1+r)^n - 1]
        # Using iterative approach to find optimal duration
        best_duration = 12  # Start with 1 year
        best_difference = float('inf')
        
        for months in range(12, 181):  # 1 to 15 years
            calculated_payment = financed_amount * (monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)
            difference = abs(calculated_payment - target_monthly_payment)
            
            if difference < best_difference:
                best_difference = difference
                best_duration = months
            
            # If we found exact match or very close, break
            if difference < 0.01:
                break
        
        # Calculate final payment with optimal duration
        final_monthly_payment = financed_amount * (monthly_rate * (1 + monthly_rate)**best_duration) / ((1 + monthly_rate)**best_duration - 1)
        years = best_duration / 12
        months = best_duration
        
    else:
        # No interest case
        final_monthly_payment = target_monthly_payment
        years = financed_amount / target_monthly_payment / 12
        months = int(years * 12)
    
    return {
        "duration_years": years,
        "duration_months": months,
        "financed_amount": round(financed_amount, 2),
        "monthly_payment": round(final_monthly_payment, 2),
        "total_interests": round((final_monthly_payment * months) - financed_amount, 2),
        "difference_vs_savings": round(final_monthly_payment - monthly_savings, 2)
    }

def calculate_all_financing_with_aids(kit_price: float, total_aids: float, monthly_savings: float, region: str = "france") -> List[Dict]:
    """
    Calculate financing options with aids deducted for all durations (3-15 years) - WITH INTERESTS
    """
    region_config = REGIONS_CONFIG.get(region, REGIONS_CONFIG["france"])
    taeg = region_config["interest_rates"]["with_aids"]
    monthly_rate = taeg / 12
    
    min_duration = region_config["financing"]["min_duration"]
    max_duration = region_config["financing"]["max_duration"]
    
    # Amount to finance after aids
    financed_amount = kit_price - total_aids
    
    options = []
    
    for years in range(min_duration, max_duration + 1):
        months = years * 12
        
        if monthly_rate > 0:
            # Standard loan calculation WITH INTERESTS
            monthly_payment_with_interests = financed_amount * (monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)
        else:
            monthly_payment_with_interests = financed_amount / months
        
        options.append({
            "duration_years": years,
            "duration_months": months,
            "monthly_payment": round(monthly_payment_with_interests, 2),
            "total_interests": round((monthly_payment_with_interests * months) - financed_amount, 2),
            "difference_vs_savings": round(monthly_payment_with_interests - monthly_savings, 2),
            "taeg": taeg
        })
    
    return options

# Routes
@api_router.get("/")
async def root():
    return {"message": "Solar Calculator API with PVGIS Integration"}

@api_router.get("/solar-kits")
async def get_solar_kits():
    """Get available solar kits with pricing"""
    return SOLAR_KITS

@api_router.post("/clients", response_model=ClientInfo)
async def create_client(client_data: ClientInfoCreate):
    try:
        # Detect region from address
        region = detect_region_from_address(client_data.address)
        
        # Geocode the address with region context
        lat, lon = await geocode_address(client_data.address, region)
        
        client_dict = client_data.dict()
        client_dict['latitude'] = lat
        client_dict['longitude'] = lon
        
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
async def calculate_solar_solution(client_id: str, region: str = "france", calculation_mode: str = "realistic", manual_kit_power: Optional[int] = None):
    try:
        # Vérifier que la région existe
        if region not in REGIONS_CONFIG:
            raise HTTPException(status_code=400, detail=f"Region '{region}' not supported")
        
        # Vérifier que le mode de calcul existe
        if calculation_mode not in CALCULATION_MODES:
            raise HTTPException(status_code=400, detail=f"Calculation mode '{calculation_mode}' not supported")
        
        client = await db.clients.find_one({"id": client_id})
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        region_config = REGIONS_CONFIG[region]
        calculation_config = CALCULATION_MODES[calculation_mode]
        
        # Extract client data
        annual_consumption = client['annual_consumption_kwh']
        roof_surface = client['roof_surface']
        orientation = client['roof_orientation']
        lat = client['latitude']
        lon = client['longitude']
        
        # Calculate optimal kit size based on region or use manual kit if provided
        if manual_kit_power:
            # Kit manuel fourni
            best_kit = manual_kit_power
            if region == "martinique":
                kit_key = f"kit_{manual_kit_power}kw"
                kit_info = region_config["kits"][kit_key]
            else:
                kit_info = SOLAR_KITS[str(manual_kit_power)]
        elif region == "martinique":
            # Pour Martinique, utiliser les kits fixes
            best_kit = calculate_optimal_kit_size_martinique(annual_consumption, roof_surface)
            kit_info = region_config["kits"][best_kit]
        else:
            # Pour France, utiliser la logique existante
            best_kit = calculate_optimal_kit_size(annual_consumption, roof_surface)
            kit_info = SOLAR_KITS[best_kit]
        
        # Get PVGIS data
        kit_power = kit_info['power'] if region == "martinique" else best_kit
        pvgis_data = await get_pvgis_data(lat, lon, orientation, kit_power)
        annual_production = pvgis_data["annual_production"]
        
        # Calculate autonomy percentage based on calculation mode
        autonomy_percentage = min(calculation_config["autonomy_cap"], (annual_production / annual_consumption) * 100)
        
        # Calculate autoconsumption using mode-specific rate
        autoconsumption_rate = calculation_config["autoconsumption_rate"]
        autoconsumption_kwh = annual_production * autoconsumption_rate
        surplus_kwh = annual_production * (1 - autoconsumption_rate)
        
        # Calculate savings with future EDF rate increases (average over 3 years)
        # Use mode-specific rate increase and surplus sale rate
        annual_rate_increase = calculation_config["annual_rate_increase"]
        surplus_sale_rate = calculation_config["surplus_sale_rate"]
        
        year1_savings = (autoconsumption_kwh * EDF_RATE_PER_KWH) + (surplus_kwh * surplus_sale_rate)
        year2_savings = year1_savings * (1 + annual_rate_increase)
        year3_savings = year2_savings * (1 + annual_rate_increase)
        avg_savings_3years = (year1_savings + year2_savings + year3_savings) / 3
        
        # Add maintenance savings (mode-specific)
        maintenance_savings = calculation_config["maintenance_savings"]  # €/year
        
        # Apply energy optimization coefficient for behavioral savings (mode-specific)
        energy_optimization_coefficient = calculation_config["optimization_coefficient"]
        
        # Calculate total annual savings
        annual_savings = (avg_savings_3years + maintenance_savings) * energy_optimization_coefficient
        monthly_savings = annual_savings / 12
        
        # Calculate real savings percentage (économies réelles par rapport à la facture EDF)
        monthly_edf_bill = client['monthly_edf_payment']
        annual_edf_bill = monthly_edf_bill * 12
        real_savings_percentage = (annual_savings / annual_edf_bill) * 100 if annual_edf_bill > 0 else 0
        
        # Calculate financing options with region-specific rates
        kit_price = kit_info['price_ttc'] if region == "martinique" else kit_info['price']
        financing_options = calculate_financing_options(kit_price, monthly_savings, region)
        
        # Calculate aids based on region
        if region == "martinique":
            # Pour Martinique, aides fixes par kit
            total_aids = kit_info['aid_amount']
            autoconsumption_aid_total = total_aids
            tva_refund = 0  # Pas de récupération TVA en Martinique
        else:
            # Pour France, calcul existant
            autoconsumption_aid_total = best_kit * AUTOCONSUMPTION_AID  # 80€/kW
            tva_refund = kit_info['price'] * TVA_RATE if best_kit > 3 else 0  # No TVA refund for 3kW
            total_aids = autoconsumption_aid_total + tva_refund
        
        # Calculate financing options with aids deducted (same duration as optimal financing)
        financing_with_aids = calculate_financing_with_aids(kit_price, total_aids, monthly_savings, region, financing_options)
        
        # Calculate all financing options with aids deducted for all durations
        all_financing_with_aids = calculate_all_financing_with_aids(kit_price, total_aids, monthly_savings, region)
        
        # Calculer le nombre de panneaux selon la région
        if region == "martinique":
            # Pour Martinique, calculer les panneaux basé sur la puissance (1 panneau = 500W)
            panel_count = kit_info['power'] * 2  # 1kW = 2 panneaux de 500W
        else:
            # Pour France, utiliser les données existantes
            panel_count = kit_info.get('panels', 0)
        
        calculation = SolarCalculation(
            client_id=client_id,
            kit_power=kit_info['power'] if region == "martinique" else best_kit,
            panel_count=panel_count,
            estimated_production=annual_production,
            estimated_savings=annual_savings,
            autonomy_percentage=autonomy_percentage,
            monthly_savings=monthly_savings,
            financing_options=financing_options,
            pvgis_annual_production=annual_production,
            pvgis_monthly_data=pvgis_data["monthly_data"].get("fixed", []) if isinstance(pvgis_data["monthly_data"], dict) else pvgis_data["monthly_data"]
        )
        
        # Update client with calculation results
        await db.clients.update_one(
            {"id": client_id},
            {"$set": {
                "recommended_kit_power": kit_info['power'] if region == "martinique" else best_kit,
                "estimated_production": annual_production,
                "estimated_savings": annual_savings,
                "pvgis_data": pvgis_data,
                "region": region,
                "calculation_mode": calculation_mode
            }}
        )
        
        # Add additional info for frontend
        result = calculation.dict()
        result.update({
            "kit_price": kit_price,
            "autoconsumption_kwh": autoconsumption_kwh,
            "surplus_kwh": surplus_kwh,
            "autoconsumption_aid": autoconsumption_aid_total,
            "tva_refund": tva_refund,
            "total_aids": total_aids,
            "financing_with_aids": financing_with_aids,
            "all_financing_with_aids": all_financing_with_aids,
            "pvgis_source": "Données source PVGIS Commission Européenne",
            "orientation": orientation,
            "coordinates": {"lat": lat, "lon": lon},
            "region": region,
            "region_config": region_config,
            "calculation_mode": calculation_mode,
            "calculation_config": calculation_config,
            "real_savings_percentage": real_savings_percentage,
            "autoconsumption_rate": autoconsumption_rate,
            "annual_edf_bill": annual_edf_bill
        })
        
        return result
        
    except Exception as e:
        logging.error(f"Calculation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def generate_monthly_chart(monthly_data: List[dict]) -> str:
    """Generate monthly production chart and return as base64"""
    try:
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Extract data
        months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
        production = [month.get('E_m', 0) for month in monthly_data]
        
        # Create bars with gradient colors
        bars = ax.bar(months, production, 
                     color=['#ff6b35' if i < 6 else '#4caf50' for i in range(len(months))],
                     alpha=0.8, edgecolor='white', linewidth=1)
        
        # Styling
        ax.set_title('Production Mensuelle Estimée (kWh)', fontsize=16, fontweight='bold', pad=20)
        ax.set_ylabel('Production (kWh)', fontsize=12, fontweight='bold')
        ax.set_xlabel('Mois', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_facecolor('#f8f9fa')
        
        # Add value labels on bars
        for bar, value in zip(bars, production):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 10,
                   f'{int(value)}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        
        # Save to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        
        chart_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return chart_base64
        
    except Exception as e:
        logging.error(f"Error generating monthly chart: {e}")
        return ""

def generate_autonomy_pie_chart(autonomy_percentage: float) -> str:
    """Generate autonomy pie chart and return as base64"""
    try:
        fig, ax = plt.subplots(figsize=(8, 8))
        
        # Data for pie chart
        autonomous = autonomy_percentage
        grid = 100 - autonomy_percentage
        
        sizes = [autonomous, grid]
        labels = [f'Autoconsommation\n{autonomous:.1f}%', f'Réseau EDF\n{grid:.1f}%']
        colors = ['#4caf50', '#ff6b35']
        explode = (0.05, 0)  # Explode autonomous part
        
        # Create pie chart
        wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels, colors=colors,
                                         autopct='%1.1f%%', shadow=True, startangle=90,
                                         textprops={'fontsize': 12, 'fontweight': 'bold'})
        
        ax.set_title('Répartition de votre Consommation Électrique', 
                    fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        # Save to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        
        chart_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return chart_base64
        
    except Exception as e:
        logging.error(f"Error generating autonomy chart: {e}")
        return ""

async def generate_solar_report_pdf(client_id: str, calculation_data: dict) -> bytes:
    """Generate comprehensive solar installation PDF report"""
    try:
        # Get client data
        client = await db.clients.find_one({"id": client_id})
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Create PDF buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                              rightMargin=50, leftMargin=50, 
                              topMargin=50, bottomMargin=50)
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2c5530'),
            alignment=1  # Center
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=12,
            textColor=colors.HexColor('#ff6b35'),
            leftIndent=0
        )
        
        # Story (content) list
        story = []
        
        # Title and header
        story.append(Paragraph("ÉTUDE SOLAIRE PERSONNALISÉE", title_style))
        story.append(Paragraph(f"<b>FRH ENVIRONNEMENT</b> - Énergie Solaire Professionnel", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Client information
        story.append(Paragraph("INFORMATIONS CLIENT", heading_style))
        client_info = [
            ['Nom complet:', f"{client['first_name']} {client['last_name']}"],
            ['Adresse:', client['address']],
            ['Surface toiture:', f"{client['roof_surface']} m²"],
            ['Orientation:', client['roof_orientation']],
            ['Système chauffage:', client['heating_system']],
            ['Consommation annuelle:', f"{client['annual_consumption_kwh']} kWh"],
            ['Facture EDF actuelle:', f"{client['monthly_edf_payment']} € / mois"],
            ['Date de l\'étude:', datetime.now().strftime('%d/%m/%Y')]
        ]
        
        client_table = Table(client_info, colWidths=[4*cm, 10*cm])
        client_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(client_table)
        story.append(Spacer(1, 20))
        
        # Solution recommendations
        story.append(Paragraph("SOLUTION RECOMMANDÉE", heading_style))
        solution_info = [
            ['Kit solaire optimal:', f"{calculation_data['kit_power']} kW ({calculation_data['panel_count']} panneaux)"],
            ['Investissement:', f"{calculation_data.get('kit_price', 0):,} € TTC"],
            ['Production annuelle estimée:', f"{calculation_data['estimated_production']:.0f} kWh"],
            ['Autonomie énergétique:', f"{calculation_data['autonomy_percentage']:.1f} %"],
            ['Économies annuelles:', f"{calculation_data['estimated_savings']:.0f} €"],
            ['Économies mensuelles:', f"{calculation_data['monthly_savings']:.0f} €"],
            ['Source données:', calculation_data.get('pvgis_source', 'PVGIS Commission Européenne')]
        ]
        
        solution_table = Table(solution_info, colWidths=[6*cm, 8*cm])
        solution_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f5e8')),
            ('BACKGROUND', (1, 4), (1, 5), colors.HexColor('#d4edda')),  # Highlight savings
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#4caf50')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(solution_table)
        story.append(Spacer(1, 30))
        
        # Financial analysis
        story.append(Paragraph("ANALYSE FINANCIÈRE", heading_style))
        
        # Aids and financing
        aids_info = [
            ['Prime autoconsommation EDF:', f"{calculation_data.get('autoconsumption_aid', 0)} €"],
            ['TVA remboursée (20%):', f"{calculation_data.get('tva_refund', 0):.0f} €"],
            ['Total des aides:', f"{calculation_data.get('total_aids', 0):.0f} €"],
            ['Reste à financer:', f"{calculation_data.get('kit_price', 0) - calculation_data.get('total_aids', 0):,.0f} €"]
        ]
        
        aids_table = Table(aids_info, colWidths=[8*cm, 6*cm])
        aids_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#fff3e0')),
            ('BACKGROUND', (1, 2), (1, 2), colors.HexColor('#4caf50')),  # Highlight total aids
            ('TEXTCOLOR', (1, 2), (1, 2), colors.white),
            ('FONTNAME', (1, 2), (1, 2), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#ff9800')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(aids_table)
        story.append(Spacer(1, 20))
        
        # Financing options
        if calculation_data.get('financing_options'):
            story.append(Paragraph("OPTIONS DE FINANCEMENT", heading_style))
            finance_data = [['Durée', 'Mensualité', 'Économie mensuelle', 'Différence']]
            
            for option in calculation_data['financing_options']:  # Show all options (6-15 years)
                difference = option['difference_vs_savings']
                diff_text = f"+{difference:.0f} €" if difference > 0 else f"{difference:.0f} €"
                finance_data.append([
                    f"{option['duration_years']} ans",
                    f"{option['monthly_payment']:.0f} €",
                    f"{calculation_data['monthly_savings']:.0f} €",
                    diff_text
                ])
            
            finance_table = Table(finance_data, colWidths=[3*cm, 3*cm, 4*cm, 4*cm])
            finance_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2196f3')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            
            story.append(finance_table)
            story.append(Spacer(1, 20))
        
        # Financing options with aids deducted
        if calculation_data.get('all_financing_with_aids'):
            story.append(Paragraph("OPTIONS DE FINANCEMENT AVEC AIDES DÉDUITES", heading_style))
            finance_aids_data = [['Durée', 'Mensualité', 'Économie mensuelle', 'Différence']]
            
            for option in calculation_data['all_financing_with_aids']:  # Show all options (6-15 years)
                difference = option['difference_vs_savings']
                diff_text = f"+{difference:.0f} €" if difference > 0 else f"{difference:.0f} €"
                finance_aids_data.append([
                    f"{option['duration_years']} ans",
                    f"{option['monthly_payment']:.0f} €",
                    f"{calculation_data['monthly_savings']:.0f} €",
                    diff_text
                ])
            
            finance_aids_table = Table(finance_aids_data, colWidths=[3*cm, 3*cm, 4*cm, 4*cm])
            finance_aids_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4caf50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            
            story.append(finance_aids_table)
            story.append(Spacer(1, 20))
        
        # Add page break
        story.append(Spacer(1, 50))
        
        # Monthly production if available
        if calculation_data.get('pvgis_monthly_data'):
            story.append(Paragraph("PRODUCTION MENSUELLE DÉTAILLÉE", heading_style))
            
            monthly_chart_b64 = generate_monthly_chart(calculation_data['pvgis_monthly_data'])
            if monthly_chart_b64:
                # Create image from base64
                chart_buffer = io.BytesIO(base64.b64decode(monthly_chart_b64))
                chart_image = Image(chart_buffer, width=12*cm, height=6*cm)
                story.append(chart_image)
                story.append(Spacer(1, 20))
        
        # Autonomy chart
        autonomy_chart_b64 = generate_autonomy_pie_chart(calculation_data['autonomy_percentage'])
        if autonomy_chart_b64:
            story.append(Paragraph("RÉPARTITION DE VOTRE CONSOMMATION", heading_style))
            autonomy_buffer = io.BytesIO(base64.b64decode(autonomy_chart_b64))
            autonomy_image = Image(autonomy_buffer, width=8*cm, height=6*cm)
            story.append(autonomy_image)
            story.append(Spacer(1, 20))
        
        # Technical specifications
        story.append(Paragraph("SPÉCIFICATIONS TECHNIQUES", heading_style))
        tech_specs = [
            ['Panneaux photovoltaïques:', f'{calculation_data["panel_count"]} × 500W monocristallin'],
            ['Puissance totale:', f'{calculation_data["kit_power"]} kWc'],
            ['Surface nécessaire:', f'{calculation_data["panel_count"] * 2.1:.1f} m²'],
            ['Onduleur:', 'Hoymiles haute performance (99,8% efficacité)'],
            ['Garantie panneaux:', '25 ans sur la production'],
            ['Garantie installation:', '10 ans décennale'],
            ['Système de montage:', 'Intégration toiture avec étanchéité'],
            ['Suivi production:', 'Application mobile temps réel']
        ]
        
        tech_table = Table(tech_specs, colWidths=[6*cm, 8*cm])
        tech_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f8ff')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#2196f3')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(tech_table)
        story.append(Spacer(1, 30))
        
        # Footer with contact info
        story.append(Paragraph("COORDONNÉES ET CONTACT", heading_style))
        footer_text = """
        <b>FRH ENVIRONNEMENT</b><br/>
        196 Avenue Jean Lolive, 93500 Pantin<br/>
        Téléphone: 09 85 60 50 51<br/>
        Email: contact@francerenovhabitat.com<br/><br/>
        
        <b>Certifications:</b><br/>
        • RGE QualiPV 2025 (Photovoltaïque)<br/>
        • RGE QualiPac 2025 (Pompes à chaleur)<br/>
        • Membre FFB (Fédération Française du Bâtiment)<br/>
        • Partenaire Agir Plus EDF<br/>
        • Garantie décennale MMA<br/><br/>
        
        <i>Ce devis est valable 30 jours. Les données de production sont basées sur les statistiques officielles PVGIS de la Commission Européenne.</i>
        """
        
        story.append(Paragraph(footer_text, styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer.getvalue()
        
    except Exception as e:
        logging.error(f"Error generating PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

def generate_devis_pdf(client_data: dict, calculation_data: dict, region: str = "france"):
    """Generate devis PDF exactly matching the original format with FRH logo and green colors"""
    try:
        buffer = io.BytesIO()
        # Marges très réduites pour plus d'espace
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=10, leftMargin=10, topMargin=10, bottomMargin=10)
        story = []
        
        # Styles
        styles = getSampleStyleSheet()
        
        # Couleur verte FRH
        frh_green = colors.HexColor('#7CB342')
        
        # Triangle vert en haut à droite (style décoratif)
        triangle_style = ParagraphStyle(
            'Triangle',
            parent=styles['Normal'],
            fontSize=20,
            textColor=frh_green,
            alignment=2  # Right align
        )
        
        # Récupérer le logo FRH depuis l'URL
        logo_url = "https://cdn-dhoin.nitrocdn.com/EuBhgITwlcEgvZudhGdVBYWQskHAaTgE/assets/images/optimized/rev-a144ac5/france-renovhabitat.fr/contenu/2021/uploads/2021/05/FRH2-logo-HORIZONTALE.png"
        try:
            logo_response = requests.get(logo_url)
            if logo_response.status_code == 200:
                logo_image = ImageReader(io.BytesIO(logo_response.content))
                logo_img = Image(logo_image, width=3*cm, height=1*cm)
            else:
                # Fallback si l'image ne peut pas être chargée
                logo_img = Paragraph("🌳 FRH ENVIRONNEMENT", styles['Normal'])
        except Exception as e:
            # Fallback si l'image ne peut pas être chargée
            logo_img = Paragraph("🌳 FRH ENVIRONNEMENT", styles['Normal'])
        
        # En-tête avec vrai logo FRH
        header_data = [
            [logo_img, f'▲ DEVIS N° : {generate_devis_number()}']
        ]
        
        header_table = Table(header_data, colWidths=[10*cm, 8*cm])
        header_table.setStyle(TableStyle([
            ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (1, 0), (1, 0), 12),
            ('TEXTCOLOR', (1, 0), (1, 0), frh_green),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 3))
        
        # Tableau PAGE/DATE/CLIENT - fond vert comme l'original
        page_info_data = [
            ['PAGE', 'DATE', 'CLIENT'],
            ['1/15', datetime.now().strftime("%d/%m/%Y"), client_data["id"][:5]]
        ]
        
        page_info_table = Table(page_info_data, colWidths=[2.5*cm, 2.5*cm, 2.5*cm])
        page_info_table.setStyle(TableStyle([
            # En-tête vert avec texte blanc
            ('BACKGROUND', (0, 0), (-1, 0), frh_green),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            # Contenu blanc avec texte noir
            ('BACKGROUND', (0, 1), (-1, 1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, 1), colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        
        # Positionner le tableau à droite
        page_info_container = Table([['', page_info_table]], colWidths=[11*cm, 7*cm])
        page_info_container.setStyle(TableStyle([
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(page_info_container)
        story.append(Spacer(1, 3))
        
        # Section CLIENT avec barre verte comme l'original
        client_header_data = [['CLIENT']]
        client_header_table = Table(client_header_data, colWidths=[19*cm])
        client_header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), frh_green),
            ('TEXTCOLOR', (0, 0), (0, 0), colors.white),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, 0), 12),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (0, 0), 3),
            ('RIGHTPADDING', (0, 0), (0, 0), 3),
            ('TOPPADDING', (0, 0), (0, 0), 3),
            ('BOTTOMPADDING', (0, 0), (0, 0), 3),
        ]))
        story.append(client_header_table)
        story.append(Spacer(1, 1))
        
        # Informations entreprise et client
        region_config = REGIONS_CONFIG.get(region, REGIONS_CONFIG['france'])
        company_info = region_config['company_info']
        
        # Créer du texte avec couleurs différentes pour délai et offre
        delai_text = Paragraph('<font color="#7CB342">Délai de livraison : </font><font color="black">3 mois</font>', styles['Normal'])
        offre_text = Paragraph('<font color="#7CB342">Offre valable jusqu\'au : </font><font color="black">16/10/2025</font>', styles['Normal'])
        
        # Données client - informations de base
        company_client_info = [
            [f"{company_info['name']}", f"{client_data['first_name']} {client_data['last_name']}"],
            [f"{company_info['address']}", f"{client_data['address']}"],
            [f"Tel.: {company_info['phone']}", f"Tel.: {client_data.get('phone', 'N/A')}"],
            [f"Email : {company_info['email']}", f"E-mail: {client_data.get('email', 'N/A')}"],
            [f"N° TVA Intra : {company_info['tva']}", delai_text],
            [f"Votre interlocuteur : Maarek Philippe", offre_text],
            [f"Type de logement : Maison individuelle", ""],
            [f"Bâtiment existant de plus de 2 ans", ""]
        ]
        
        company_client_table = Table(company_client_info, colWidths=[9.5*cm, 9.5*cm])
        company_client_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 1),
            ('RIGHTPADDING', (0, 0), (-1, -1), 1),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            # Supprimer les couleurs hardcodées car elles sont maintenant dans les Paragraph
        ]))
        story.append(company_client_table)
        story.append(Spacer(1, 5))
        
        # Titre DEVIS PV MARTINIQUE - couleur verte
        title_style = ParagraphStyle(
            'DevisTitle',
            parent=styles['Heading1'],
            fontSize=14,
            fontName='Helvetica-Bold',
            textColor=frh_green,
            alignment=1,
            spaceAfter=3
        )
        story.append(Paragraph(f"DEVIS PV {region.upper()}", title_style))
        
        # Tableau des spécifications - fond vert comme l'original
        kit_power = calculation_data.get('recommended_kit_power', 6) or 6
        panel_count = calculation_data.get('panel_count', 12)
        kit_price = calculation_data.get('kit_price', 13900)
        
        # Calcul des prix
        tva_rate = 0.021 if region == 'martinique' else 0.20  # 2.1% pour Martinique, 20% pour France
        prix_ht = kit_price / (1 + tva_rate)
        tva_display = "2.10" if region == 'martinique' else "20.00"
        
        # Description technique - version compacte
        tech_description = f"""- Centrale en surimposition à la toiture de {panel_count} panneaux
photovoltaïques de la marque POWERNITY représentant une
puissance totale de {kit_power * 1000} Watt Crêtes pour de
l'autoconsommation
Modèle : JKL132-B-MH
Référence : POW500
- Puissance d'un panneau 500W
- Module solaire monocristallin haute efficacité.
Certifications
CEI: 61215, CEI 61730, CE, CQC
ISO90012015système de gestion de la qualité
ISO14001201système de management environnemental
ISO45001201système de management de la santé et de la
sécurité au travail
- La technologie SE améliore efficacement l'efficacité
de la conversion cellulaire.
- Film anti reflet optimisé, matériau d'encapsulation
pour obtenir d'excellentes performances anti-PID.
Conception MBB et demi-cellule pour réduire les effets
d'ombre, améliorer la fiabilité du module et réduire
les pertes.

- Dimensions (L*W*H) (mm)
2094×1134×30mm par panneau
- Poids (kg) : 26 par panneau
25 ans de garantie constructeur sur la puissance
linéaire
12 ans garantie constructeur-
Structure des panneaux : K2 solitrail


- 6 Micro-onduleur de la marque POWERNITY Ref : PW1000
- Boîtier AC/DC, parafoudre
- Gestion, programmation de la production d'énergie
par la centrale photovoltaïque avec le système
Powernity Solar Logiciel
Garantie constructeur Micro Onduleur : 15 ans"""
        
        # Tableau principal - fond vert comme l'original
        main_table_data = [
            ['DESIGNATION', 'QUANTITE', 'UNITE', 'P.U. HT', 'TVA', 'PRIX TTC'],
            [tech_description, '1.00', '12', f'{prix_ht:.2f} €', tva_display, f'{kit_price:.2f} €']
        ]
        
        main_table = Table(main_table_data, colWidths=[11*cm, 1.5*cm, 1.5*cm, 2*cm, 1*cm, 2*cm])
        main_table.setStyle(TableStyle([
            # En-tête vert comme l'original
            ('BACKGROUND', (0, 0), (-1, 0), frh_green),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            # Contenu
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, 1), 8),
            ('ALIGN', (0, 1), (0, 1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, 1), 'CENTER'),
            ('VALIGN', (0, 1), (-1, 1), 'TOP'),
            # Bordures noires
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('LINEWIDTH', (0, 0), (-1, -1), 1),
            # Padding réduit
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        
        story.append(main_table)
        story.append(Spacer(1, 5))
        
        # Section footer avec adresse centrée comme l'original et logo FRH en bas à droite
        try:
            # Utiliser le même logo que dans l'en-tête
            logo_response = requests.get(logo_url)
            if logo_response.status_code == 200:
                footer_logo_image = ImageReader(io.BytesIO(logo_response.content))
                footer_logo_img = Image(footer_logo_image, width=2*cm, height=0.7*cm)
            else:
                footer_logo_img = Paragraph('<font color="#7CB342" size="10">🌳 FRH</font>', styles['Normal'])
        except Exception as e:
            footer_logo_img = Paragraph('<font color="#7CB342" size="10">🌳 FRH</font>', styles['Normal'])
        
        footer_data = [
            [f'FRH {region.upper()}', ''],
            [f'{company_info["address"]}', ''],
            ['CAPITAL: 30 000 € - SIRET : 890 493 737 00013 RCS: 89049373-7- NAF: 4322B', footer_logo_img]
        ]
        
        footer_table = Table(footer_data, colWidths=[16*cm, 3*cm])
        footer_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(footer_table)
        
        # Construire le PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer.getvalue()
        
    except Exception as e:
        logging.error(f"Error generating devis PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating devis PDF: {str(e)}")

def generate_devis_number():
    """Generate unique devis number"""
    return f"{datetime.now().strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}"

@api_router.get("/generate-pdf/{client_id}")
async def generate_pdf_report(client_id: str):
    """Generate and download PDF report for client"""
    try:
        # Get client
        client = await db.clients.find_one({"id": client_id})
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Get calculation data - recalculate with correct region
        client_region = client.get('region', 'france')  # Récupérer la région du client
        calculation_response = await calculate_solar_solution(client_id, client_region)
        
        # Generate PDF
        pdf_bytes = await generate_solar_report_pdf(client_id, calculation_response)
        
        # Return PDF as response
        filename = f"etude_solaire_{client['first_name']}_{client['last_name']}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logging.error(f"PDF generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/generate-devis/{client_id}")
async def generate_devis(client_id: str, region: str = "france"):
    """Generate and download devis PDF for client"""
    try:
        # Get client
        client = await db.clients.find_one({"id": client_id})
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Get calculation data
        calculation_response = await calculate_solar_solution(client_id, region)
        
        # Generate devis PDF
        pdf_bytes = generate_devis_pdf(client, calculation_response, region)
        
        # Return PDF as response
        filename = f"devis_{client['first_name']}_{client['last_name']}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logging.error(f"Devis generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/test-pvgis/{lat}/{lon}")
async def test_pvgis(lat: float, lon: float, orientation: str = "Sud", power: int = 6):
    """Test endpoint for PVGIS API"""
    try:
        data = await get_pvgis_data(lat, lon, orientation, power)
        return {
            "coordinates": {"lat": lat, "lon": lon},
            "orientation": orientation,
            "power_kw": power,
            "pvgis_data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Modèles pour l'analyse de toiture
class RoofAnalysisRequest(BaseModel):
    image_base64: str  # Image encodée en base64
    panel_count: int   # Nombre de panneaux à positionner (6, 12, ou 18)
    panel_surface: float = 2.11  # Surface d'un panneau en m²

class PanelPosition(BaseModel):
    x: float  # Position X relative (0-1)
    y: float  # Position Y relative (0-1) 
    width: float  # Largeur relative (0-1)
    height: float  # Hauteur relative (0-1)
    angle: float  # Angle de rotation en degrés

# Endpoint supprimé - fonctionnalité d'analyse de toiture retirée pour stabilité

# Endpoints pour la gestion des régions
@api_router.get("/regions")
async def get_regions():
    """
    Récupère la liste des régions disponibles
    """
    return {
        "regions": list(REGIONS_CONFIG.keys()),
        "regions_data": {
            region: {
                "name": config["name"],
                "logo_subtitle": config["logo_subtitle"],
                "company_info": config["company_info"]
            }
            for region, config in REGIONS_CONFIG.items()
        }
    }

@api_router.get("/regions/{region_name}")
async def get_region_config(region_name: str):
    """
    Récupère la configuration complète d'une région
    """
    if region_name not in REGIONS_CONFIG:
        raise HTTPException(status_code=404, detail=f"Region '{region_name}' not found")
    
    return {
        "region": region_name,
        "config": REGIONS_CONFIG[region_name]
    }

@api_router.get("/regions/{region_name}/kits")
async def get_region_kits(region_name: str):
    """
    Récupère les kits disponibles pour une région
    """
    if region_name not in REGIONS_CONFIG:
        raise HTTPException(status_code=404, detail=f"Region '{region_name}' not found")
    
    region_config = REGIONS_CONFIG[region_name]
    
    if region_name == "martinique":
        # Retourner les kits fixes de Martinique
        kits = []
        for kit_id, kit_data in region_config["kits"].items():
            kits.append({
                "id": kit_id,
                "name": kit_data["description"],
                "power": kit_data["power"],
                "price_ht": kit_data["price_ttc"],  # Prix TTC pour Martinique
                "price_ttc": kit_data["price_ttc"],
                "aid_amount": kit_data["aid_amount"],
                "surface": kit_data["surface"],
                "co2_savings": kit_data["price_ttc"] * 0.15  # 15% comme commission CO2
            })
        return {"kits": kits}
    else:
        # Pour la France, récupérer les kits depuis la base de données (logique existante)
        kits = db.kits.find()
        kits_list = await kits.to_list(length=100)
        
        # Convertir ObjectId en string pour JSON
        for kit in kits_list:
            kit["_id"] = str(kit["_id"])
            
        return {"kits": kits_list}

# Endpoints pour la gestion des modes de calcul
@api_router.get("/calculation-modes")
async def get_calculation_modes():
    """
    Récupère la liste des modes de calcul disponibles
    """
    return {
        "modes": {
            mode: {
                "name": config["name"],
                "description": config["description"]
            }
            for mode, config in CALCULATION_MODES.items()
        }
    }

@api_router.get("/calculation-modes/{mode_name}")
async def get_calculation_mode_config(mode_name: str):
    """
    Récupère la configuration complète d'un mode de calcul
    """
    if mode_name not in CALCULATION_MODES:
        raise HTTPException(status_code=404, detail=f"Calculation mode '{mode_name}' not found")
    
    return {
        "mode": mode_name,
        "config": CALCULATION_MODES[mode_name]
    }

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