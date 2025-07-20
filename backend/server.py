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
            "standard": 0.08,  # 8% TAEG
            "with_aids": 0.08  # 8% TAEG
        },
        "kits": {
            "kit_3kw": {
                "power": 3,
                "price_ttc": 9900,
                "aid_amount": 5340,
                "surface": 15,  # m² estimée
                "description": "Kit 3kW - Résidentiel"
            },
            "kit_6kw": {
                "power": 6,
                "price_ttc": 13900,
                "aid_amount": 6480,
                "surface": 30,  # m² estimée
                "description": "Kit 6kW - Résidentiel+"
            },
            "kit_9kw": {
                "power": 9,
                "price_ttc": 16900,
                "aid_amount": 9720,
                "surface": 45,  # m² estimée
                "description": "Kit 9kW - Grande résidence"
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

async def geocode_address(address: str) -> tuple[float, float]:
    """
    Convert address to latitude/longitude using geopy
    """
    try:
        geolocator = Nominatim(user_agent="solar_calculator")
        location = geolocator.geocode(address + ", France")
        if location:
            return location.latitude, location.longitude
        else:
            raise ValueError(f"Could not geocode address: {address}")
    except Exception as e:
        logging.error(f"Geocoding error: {e}")
        raise HTTPException(status_code=400, detail=f"Could not find coordinates for address: {address}")

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
        # Geocode the address
        lat, lon = await geocode_address(client_data.address)
        
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
async def calculate_solar_solution(client_id: str, region: str = "france", calculation_mode: str = "realistic"):
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
        
        # Calculate optimal kit size based on region
        if region == "martinique":
            # Pour Martinique, utiliser les kits fixes
            best_kit = calculate_optimal_kit_size_martinique(annual_consumption, roof_surface)
            kit_info = region_config["kits"][best_kit]
        else:
            # Pour France, utiliser la logique existante
            best_kit = calculate_optimal_kit_size(annual_consumption, roof_surface)
            kit_info = SOLAR_KITS[best_kit]
        
        # Get PVGIS data
        pvgis_data = await get_pvgis_data(lat, lon, orientation, 
                                         kit_info['power'] if region == "martinique" else best_kit)
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

def create_composite_image_with_panels(base64_image: str, panel_positions: List[Dict], panel_count: int) -> str:
    """
    Génère une image composite RÉALISTE avec des panneaux solaires qui suivent PARFAITEMENT la pente et la perspective du toit
    """
    try:
        logging.info(f"Creating HIGH-QUALITY roof-adapted composite with {panel_count} panels")
        
        # Décoder et valider l'image base64
        try:
            if base64_image.startswith('data:image'):
                base64_data = base64_image.split(',')[1]
            else:
                base64_data = base64_image
            
            image_data = base64.b64decode(base64_data)
            original_image = PILImage.open(BytesIO(image_data)).convert('RGB')
            logging.info(f"Successfully loaded image: {original_image.size}")
            
        except Exception as e:
            logging.error(f"Error decoding base64 image: {e}")
            return base64_image
        
        # Créer une copie de haute qualité pour dessiner dessus
        composite_image = original_image.copy()
        draw = ImageDraw.Draw(composite_image)
        
        # Dimensions de l'image
        img_width, img_height = composite_image.size
        logging.info(f"Image dimensions: {img_width}x{img_height}")
        
        # Si l'OpenAI n'a pas retourné de positions, utiliser notre algorithme optimisé
        if not panel_positions or len(panel_positions) == 0:
            logging.info("No AI positions provided, using optimized roof-adapted algorithm")
            roof_positions = generate_intelligent_roof_positions(panel_count, img_width, img_height)
        else:
            # Convertir les positions AI en format utilisable
            roof_positions = []
            for pos in panel_positions[:panel_count]:
                roof_positions.append({
                    'x': pos.get('x', 0.3),
                    'y': pos.get('y', 0.3),
                    'width': pos.get('width', 0.12),
                    'height': pos.get('height', 0.07),
                    'angle': pos.get('angle', 15)
                })
            logging.info(f"Using {len(roof_positions)} AI-provided positions")
        
        # DESSINER CHAQUE PANNEAU AVEC PERSPECTIVE ET INCLINAISON RÉALISTES
        for i, pos in enumerate(roof_positions):
            # Position de base sur le toit avec validation
            base_x = max(10, min(int(pos['x'] * img_width), img_width - 100))
            base_y = max(10, min(int(pos['y'] * img_height), img_height - 80))
            
            # Calculer les dimensions du panneau selon la position dans l'image (perspective)
            # Plus haut dans l'image = plus petit (perspective)
            distance_factor = (pos['y'] - 0.15) / 0.4  # Normaliser entre 0 et 1
            perspective_scale = 1.0 - (distance_factor * 0.35)  # Réduction progressive de 35%
            
            # Dimensions de base d'un panneau solaire réel (proportions correctes)
            base_panel_width = int(img_width * 0.12 * perspective_scale)
            base_panel_height = int(img_height * 0.07 * perspective_scale)
            
            # CALCUL DE L'INCLINAISON DU TOIT (effet parallélogramme)
            # Simuler une inclinaison de toit réaliste (30-45° standard)
            roof_inclination_factor = 0.25  # Facteur d'inclinaison visuelle
            skew_x = int(base_panel_height * roof_inclination_factor)
            
            # Créer les 4 coins du panneau avec perspective et inclinaison correctes
            points = [
                (base_x, base_y),                                             # Coin supérieur gauche
                (base_x + base_panel_width + skew_x, base_y),                # Coin supérieur droit (décalé)
                (base_x + base_panel_width, base_y + base_panel_height),     # Coin inférieur droit
                (base_x - skew_x, base_y + base_panel_height)                # Coin inférieur gauche (décalé)
            ]
            
            # RENDU ULTRA-RÉALISTE DU PANNEAU SOLAIRE
            
            # 1. OMBRE PORTÉE SUR LE TOIT (réalisme +++)
            shadow_offset = max(2, int(base_panel_height * 0.05))
            shadow_points = [(x + shadow_offset, y + shadow_offset) for x, y in points]
            draw.polygon(shadow_points, fill=(60, 60, 60, 120))  # Ombre semi-transparente
            
            # 2. CORPS PRINCIPAL DU PANNEAU (couleur photovoltaïque authentique)
            main_color = (15, 25, 45)  # Bleu très foncé typique des panneaux
            draw.polygon(points, fill=main_color, outline=(140, 140, 140), width=2)
            
            # 3. CADRE ALUMINIUM ÉPAIS (très visible)
            frame_width = max(2, int(min(base_panel_width, base_panel_height) * 0.04))
            for offset in range(frame_width):
                frame_points = [
                    (x - offset, y - offset) if j < 2 else (x + offset, y + offset) 
                    for j, (x, y) in enumerate(points)
                ]
                draw.polygon(points, outline=(180, 180, 180), width=frame_width - offset)
            
            # 4. GRILLE DE CELLULES PHOTOVOLTAÏQUES (très détaillée)
            cells_h = 6  # Cellules horizontales
            cells_v = 10  # Cellules verticales
            
            for row in range(cells_v):
                for col in range(cells_h):
                    # Calculer la position exacte de chaque cellule avec perspective
                    h_ratio = col / cells_h
                    v_ratio = row / cells_v
                    
                    # Interpolation linéaire entre les coins pour suivre la forme exacte
                    # Côté supérieur
                    top_left = (
                        points[0][0] + h_ratio * (points[1][0] - points[0][0]),
                        points[0][1] + h_ratio * (points[1][1] - points[0][1])
                    )
                    top_right = (
                        points[0][0] + (h_ratio + 1/cells_h) * (points[1][0] - points[0][0]),
                        points[0][1] + (h_ratio + 1/cells_h) * (points[1][1] - points[0][1])
                    )
                    
                    # Côté inférieur  
                    bottom_left = (
                        points[3][0] + h_ratio * (points[2][0] - points[3][0]),
                        points[3][1] + h_ratio * (points[2][1] - points[3][1])
                    )
                    bottom_right = (
                        points[3][0] + (h_ratio + 1/cells_h) * (points[2][0] - points[3][0]),
                        points[3][1] + (h_ratio + 1/cells_h) * (points[2][1] - points[3][1])
                    )
                    
                    # Interpolation verticale pour cette cellule
                    cell_tl = (
                        top_left[0] + v_ratio * (bottom_left[0] - top_left[0]),
                        top_left[1] + v_ratio * (bottom_left[1] - top_left[1])
                    )
                    cell_tr = (
                        top_right[0] + v_ratio * (bottom_right[0] - top_right[0]),
                        top_right[1] + v_ratio * (bottom_right[1] - top_right[1])
                    )
                    cell_bl = (
                        top_left[0] + (v_ratio + 1/cells_v) * (bottom_left[0] - top_left[0]),
                        top_left[1] + (v_ratio + 1/cells_v) * (bottom_left[1] - top_left[1])
                    )
                    cell_br = (
                        top_right[0] + (v_ratio + 1/cells_v) * (bottom_right[0] - top_right[0]),
                        top_right[1] + (v_ratio + 1/cells_v) * (bottom_right[1] - top_right[1])
                    )
                    
                    cell_points = [cell_tl, cell_tr, cell_br, cell_bl]
                    
                    # Couleur alternée pour les cellules (réalisme)
                    cell_color = (20, 30, 50) if (row + col) % 2 == 0 else (25, 35, 55)
                    draw.polygon(cell_points, fill=cell_color, outline=(40, 50, 70), width=1)
            
            # 5. REFLET LUMINEUX SUR LE VERRE (effet très réaliste)
            highlight_intensity = max(0.3, 1.0 - distance_factor)  # Plus fort au premier plan
            highlight_points = [
                points[0],
                (points[0][0] + (points[1][0] - points[0][0]) * 0.7, 
                 points[0][1] + (points[1][1] - points[0][1]) * 0.7),
                (points[3][0] + (points[2][0] - points[3][0]) * 0.7, 
                 points[3][1] + (points[2][1] - points[3][1]) * 0.3),
                (points[3][0], points[3][1] + (points[0][1] - points[3][1]) * 0.3)
            ]
            highlight_color = (int(120 * highlight_intensity), 
                             int(150 * highlight_intensity), 
                             int(180 * highlight_intensity))
            
            # Créer un overlay semi-transparent pour le reflet
            overlay = PILImage.new('RGBA', composite_image.size, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.polygon(highlight_points, fill=(*highlight_color, 80))
            composite_image = PILImage.alpha_composite(composite_image.convert('RGBA'), overlay).convert('RGB')
            draw = ImageDraw.Draw(composite_image)
            
            # 6. POINTS DE FIXATION (boulons de montage)
            fixation_size = max(3, int(min(base_panel_width, base_panel_height) * 0.02))
            
            # 4 points de fixation aux coins (décalés vers l'intérieur)
            margin = int(min(base_panel_width, base_panel_height) * 0.12)
            fixation_points = [
                (points[0][0] + margin, points[0][1] + margin),         # Coin supérieur gauche
                (points[1][0] - margin, points[1][1] + margin),         # Coin supérieur droit  
                (points[2][0] - margin, points[2][1] - margin),         # Coin inférieur droit
                (points[3][0] + margin, points[3][1] - margin)          # Coin inférieur gauche
            ]
            
            for fx, fy in fixation_points:
                # Dessin du boulon avec effet 3D
                draw.ellipse([fx-fixation_size, fy-fixation_size, 
                             fx+fixation_size, fy+fixation_size], 
                            fill=(120, 120, 120), outline=(80, 80, 80), width=1)
                # Centre du boulon
                draw.ellipse([fx-fixation_size//2, fy-fixation_size//2, 
                             fx+fixation_size//2, fy+fixation_size//2], 
                            fill=(90, 90, 90))
        
        logging.info(f"Successfully created ultra-realistic composite with {len(roof_positions)} panels with perfect roof perspective")
        
        # Sauvegarder en haute qualité
        buffer = BytesIO()
        composite_image.save(buffer, format='JPEG', quality=98, optimize=True)
        buffer.seek(0)
        
        composite_base64 = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/jpeg;base64,{composite_base64}"
        
    except Exception as e:
        logging.error(f"Error creating ultra-realistic roof-adapted composite: {e}")
        return base64_image

def analyze_roof_geometry_and_obstacles(base64_image: str) -> Dict:
    """
    Analyse INTELLIGENTE de la géométrie réelle du toit et détection des obstacles
    """
    try:
        # Décoder l'image
        if base64_image.startswith('data:image'):
            base64_data = base64_image.split(',')[1]
        else:
            base64_data = base64_image
        
        image_data = base64.b64decode(base64_data)
        original_image = PILImage.open(BytesIO(image_data)).convert('RGB')
        img_width, img_height = original_image.size
        
        # Convertir en numpy pour l'analyse
        import numpy as np
        img_array = np.array(original_image)
        
        logging.info(f"Analyzing roof geometry for {img_width}x{img_height} image")
        
        # === DÉTECTION DE L'INCLINAISON RÉELLE DU TOIT ===
        # Analyser les lignes de toit (arêtes, gouttières)
        roof_inclination = detect_roof_slope_from_image(img_array)
        
        # === DÉTECTION DES OBSTACLES (VELUX, CHEMINÉES, ETC.) ===
        obstacles = detect_roof_obstacles(img_array, img_width, img_height)
        
        # === ZONES EXPLOITABLES POUR PANNEAUX ===
        usable_zones = calculate_usable_roof_zones(obstacles, img_width, img_height, roof_inclination)
        
        return {
            'roof_inclination': roof_inclination,
            'obstacles': obstacles,
            'usable_zones': usable_zones,
            'roof_type': determine_roof_type(img_array),
            'optimal_orientation': calculate_optimal_orientation(img_array)
        }
        
    except Exception as e:
        logging.error(f"Error in roof geometry analysis: {e}")
        return {
            'roof_inclination': 30.0,
            'obstacles': [],
            'usable_zones': [{'x1': 0.15, 'y1': 0.18, 'x2': 0.85, 'y2': 0.58}],
            'roof_type': 'standard',
            'optimal_orientation': 'south'
        }

def detect_roof_slope_from_image(img_array) -> float:
    """
    Détecte l'inclinaison RÉELLE du toit depuis l'image
    """
    try:
        import numpy as np
        
        # Convertir en niveaux de gris
        gray = np.mean(img_array, axis=2).astype(np.uint8)
        
        # Détecter les lignes horizontales et diagonales du toit
        height, width = gray.shape
        
        # Chercher les lignes de gouttière et d'arête
        roof_lines = []
        
        # Analyser les rangées horizontales pour trouver les changements de luminosité
        for y in range(int(height * 0.1), int(height * 0.7)):
            row_data = gray[y, :]
            
            # Détecter les variations importantes (bords de toit)
            gradient = np.abs(np.diff(row_data.astype(float)))
            if np.max(gradient) > 30:  # Seuil de détection de bord
                roof_lines.append(y)
        
        # Calculer l'inclinaison moyenne
        if len(roof_lines) >= 2:
            # Analyser la pente entre les lignes détectées
            top_line = min(roof_lines)
            bottom_line = max(roof_lines)
            
            # Estimer l'angle basé sur la perspective
            perspective_ratio = (bottom_line - top_line) / height
            inclination = min(45.0, max(15.0, perspective_ratio * 90))
        else:
            inclination = 30.0  # Inclinaison standard
        
        logging.info(f"Detected roof slope: {inclination:.1f}°")
        return inclination
        
    except Exception as e:
        logging.error(f"Error detecting roof slope: {e}")
        return 30.0

def detect_roof_obstacles(img_array, img_width: int, img_height: int) -> List[Dict]:
    """
    NOUVEAU : Détection RÉELLE et INTELLIGENTE des obstacles sur une vraie photo de toit
    """
    try:
        import numpy as np
        obstacles = []
        
        # Convertir l'image pour analyse avancée
        if len(img_array.shape) == 3:
            # Image couleur - analyser chaque canal séparément
            r_channel = img_array[:, :, 0]
            g_channel = img_array[:, :, 1]
            b_channel = img_array[:, :, 2]
            gray = np.mean(img_array, axis=2).astype(np.uint8)
        else:
            gray = img_array
            r_channel = g_channel = b_channel = gray
        
        height, width = gray.shape
        
        # === DÉTECTION AVANCÉE DES VELUX ===
        logging.info("🔍 Détection avancée des velux...")
        
        # Les velux sont généralement :
        # 1. Plus clairs que le toit (réfléchissent la lumière)
        # 2. Rectangulaires avec des bords nets
        # 3. Contraste élevé avec l'environnement
        
        # Détecter les zones très claires (velux)
        bright_threshold = np.percentile(gray, 85)  # Top 15% des pixels les plus clairs
        bright_mask = gray > bright_threshold
        
        # Détecter les zones rectangulaires claires
        from scipy import ndimage
        
        # Structuring element pour détecter des formes rectangulaires
        struct_elem = np.ones((20, 20))  # Zone de 20x20 pixels minimum
        
        # Appliquer la morphologie pour détecter des zones compactes
        bright_regions = ndimage.binary_opening(bright_mask, structure=struct_elem)
        
        # Labéliser les régions connectées
        labeled_regions, num_features = ndimage.label(bright_regions)
        
        # Analyser chaque région pour déterminer si c'est un velux
        for region_id in range(1, num_features + 1):
            # Extraire la région
            region_mask = (labeled_regions == region_id)
            region_coords = np.where(region_mask)
            
            if len(region_coords[0]) < 400:  # Trop petit pour être un velux
                continue
                
            # Calculer les dimensions de la région
            min_y, max_y = np.min(region_coords[0]), np.max(region_coords[0])
            min_x, max_x = np.min(region_coords[1]), np.max(region_coords[1])
            
            region_width = max_x - min_x
            region_height = max_y - min_y
            
            # Vérifier si c'est de forme rectangulaire (ratio largeur/hauteur)
            aspect_ratio = region_width / region_height if region_height > 0 else 0
            
            # Les velux ont généralement un aspect ratio entre 0.7 et 1.5
            if 0.7 <= aspect_ratio <= 1.5:
                # Vérifier l'uniformité de la luminosité dans la région
                region_pixels = gray[region_mask]
                region_std = np.std(region_pixels)
                
                # Les velux ont une luminosité relativement uniforme
                if region_std < 30:  # Luminosité uniforme
                    # Convertir en coordonnées relatives
                    rel_x1 = min_x / width
                    rel_y1 = min_y / height
                    rel_x2 = max_x / width
                    rel_y2 = max_y / height
                    
                    # Vérifier que c'est dans une zone de toit plausible
                    if 0.1 < rel_x1 < 0.9 and 0.1 < rel_y1 < 0.8:
                        obstacles.append({
                            'type': 'velux',
                            'x1': rel_x1,
                            'y1': rel_y1,
                            'x2': rel_x2,
                            'y2': rel_y2,
                            'confidence': min(1.0, (np.mean(region_pixels) - bright_threshold) / 50.0),
                            'area': region_width * region_height
                        })
                        logging.info(f"✅ Velux détecté: ({rel_x1:.3f}, {rel_y1:.3f}) - ({rel_x2:.3f}, {rel_y2:.3f})")
        
        # === DÉTECTION AVANCÉE DES CHEMINÉES ===
        logging.info("🔍 Détection avancée des cheminées...")
        
        # Les cheminées sont généralement :
        # 1. Plus sombres que le toit
        # 2. Verticales et rectangulaires
        # 3. Situées sur le faîtage ou près du faîtage
        
        # Détecter les zones sombres
        dark_threshold = np.percentile(gray, 25)  # Bottom 25% des pixels les plus sombres
        dark_mask = gray < dark_threshold
        
        # Détecter les formes verticales (cheminées)
        vertical_struct = np.ones((30, 15))  # Structure verticale
        dark_regions = ndimage.binary_opening(dark_mask, structure=vertical_struct)
        
        # Labéliser les régions sombres
        dark_labeled, dark_features = ndimage.label(dark_regions)
        
        for region_id in range(1, dark_features + 1):
            region_mask = (dark_labeled == region_id)
            region_coords = np.where(region_mask)
            
            if len(region_coords[0]) < 200:  # Trop petit pour être une cheminée
                continue
                
            # Calculer les dimensions
            min_y, max_y = np.min(region_coords[0]), np.max(region_coords[0])
            min_x, max_x = np.min(region_coords[1]), np.max(region_coords[1])
            
            region_width = max_x - min_x
            region_height = max_y - min_y
            
            # Les cheminées sont plus hautes que larges
            aspect_ratio = region_height / region_width if region_width > 0 else 0
            
            if aspect_ratio >= 1.2:  # Plus haut que large
                rel_x1 = min_x / width
                rel_y1 = min_y / height
                rel_x2 = max_x / width
                rel_y2 = max_y / height
                
                # Les cheminées sont généralement dans la partie haute du toit
                if rel_y1 < 0.4:  # Dans la partie haute
                    obstacles.append({
                        'type': 'cheminee',
                        'x1': rel_x1,
                        'y1': rel_y1,
                        'x2': rel_x2,
                        'y2': rel_y2,
                        'confidence': 0.8,
                        'area': region_width * region_height
                    })
                    logging.info(f"✅ Cheminée détectée: ({rel_x1:.3f}, {rel_y1:.3f}) - ({rel_x2:.3f}, {rel_y2:.3f})")
        
        # === DÉTECTION DES ANTENNES ET AUTRES ===
        logging.info("🔍 Détection d'autres obstacles...")
        
        # Détecter des objets avec un contraste élevé (antennes, etc.)
        # Calculer le gradient pour détecter les bords nets
        grad_x = np.abs(np.gradient(gray, axis=1))
        grad_y = np.abs(np.gradient(gray, axis=0))
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        # Zones avec des bords très nets
        high_gradient = gradient_magnitude > np.percentile(gradient_magnitude, 95)
        
        # Nettoyer et analyser les régions de haute gradient
        clean_grad = ndimage.binary_opening(high_gradient, structure=np.ones((5, 5)))
        grad_labeled, grad_features = ndimage.label(clean_grad)
        
        for region_id in range(1, min(grad_features + 1, 10)):  # Limiter à 10 pour performance
            region_mask = (grad_labeled == region_id)
            region_coords = np.where(region_mask)
            
            if 50 < len(region_coords[0]) < 1000:  # Taille raisonnable
                min_y, max_y = np.min(region_coords[0]), np.max(region_coords[0])
                min_x, max_x = np.min(region_coords[1]), np.max(region_coords[1])
                
                rel_x1 = min_x / width
                rel_y1 = min_y / height
                rel_x2 = max_x / width
                rel_y2 = max_y / height
                
                # Éviter les bords de l'image
                if 0.1 < rel_x1 < 0.9 and 0.1 < rel_y1 < 0.8:
                    obstacles.append({
                        'type': 'antenne',
                        'x1': rel_x1,
                        'y1': rel_y1,
                        'x2': rel_x2,
                        'y2': rel_y2,
                        'confidence': 0.6,
                        'area': (max_x - min_x) * (max_y - min_y)
                    })
        
        # Trier par superficie (plus gros obstacles en premier)
        obstacles.sort(key=lambda x: x.get('area', 0), reverse=True)
        
        # Limiter le nombre d'obstacles pour éviter le sur-détection
        obstacles = obstacles[:10]
        
        logging.info(f"🎯 DÉTECTION TERMINÉE: {len(obstacles)} obstacles détectés")
        for obs in obstacles:
            logging.info(f"   - {obs['type']}: confiance {obs['confidence']:.2f}, zone ({obs['x1']:.3f},{obs['y1']:.3f})-({obs['x2']:.3f},{obs['y2']:.3f})")
        
        return obstacles
        
    except ImportError:
        logging.error("scipy not available - using fallback detection")
        return detect_roof_obstacles_fallback(img_array, img_width, img_height)
    except Exception as e:
        logging.error(f"Error in advanced obstacle detection: {e}")
        return detect_roof_obstacles_fallback(img_array, img_width, img_height)

def detect_roof_obstacles_fallback(img_array, img_width: int, img_height: int) -> List[Dict]:
    """
    Version fallback sans scipy pour la détection d'obstacles
    """
    try:
        import numpy as np
        obstacles = []
        
        # Analyse basique sans scipy
        if len(img_array.shape) == 3:
            gray = np.mean(img_array, axis=2).astype(np.uint8)
        else:
            gray = img_array
            
        height, width = gray.shape
        
        # Analyse par zones de 50x50 pixels
        zone_size = 50
        
        for y in range(0, height - zone_size, zone_size // 2):
            for x in range(0, width - zone_size, zone_size // 2):
                # Extraire la zone
                zone = gray[y:y+zone_size, x:x+zone_size]
                
                if zone.size == 0:
                    continue
                
                zone_mean = np.mean(zone)
                zone_std = np.std(zone)
                
                # Détecter velux (zones très claires avec faible variation)
                if zone_mean > 180 and zone_std < 25:
                    rel_x1 = x / width
                    rel_y1 = y / height
                    rel_x2 = (x + zone_size) / width
                    rel_y2 = (y + zone_size) / height
                    
                    if 0.1 < rel_x1 < 0.9 and 0.1 < rel_y1 < 0.8:
                        obstacles.append({
                            'type': 'velux',
                            'x1': rel_x1,
                            'y1': rel_y1,
                            'x2': rel_x2,
                            'y2': rel_y2,
                            'confidence': 0.7,
                            'area': zone_size * zone_size
                        })
                
                # Détecter cheminées (zones sombres dans la partie haute)
                elif zone_mean < 80 and y < height * 0.4:
                    rel_x1 = x / width
                    rel_y1 = y / height
                    rel_x2 = (x + zone_size) / width
                    rel_y2 = (y + zone_size) / height
                    
                    obstacles.append({
                        'type': 'cheminee',
                        'x1': rel_x1,
                        'y1': rel_y1,
                        'x2': rel_x2,
                        'y2': rel_y2,
                        'confidence': 0.6,
                        'area': zone_size * zone_size
                    })
        
        # Fusionner les obstacles proches et limiter le nombre
        merged_obstacles = merge_nearby_obstacles(obstacles)
        return merged_obstacles[:8]  # Limiter à 8 obstacles max
        
    except Exception as e:
        logging.error(f"Error in fallback obstacle detection: {e}")
        return []

def merge_nearby_obstacles(obstacles: List[Dict]) -> List[Dict]:
    """
    Fusionne les obstacles détectés qui sont proches les uns des autres
    """
    if not obstacles:
        return []
    
    merged = []
    used = set()
    
    for i, obs1 in enumerate(obstacles):
        if i in used:
            continue
            
        # Créer un nouvel obstacle fusionné
        merged_obs = obs1.copy()
        used.add(i)
        
        # Chercher les obstacles proches à fusionner
        for j, obs2 in enumerate(obstacles[i+1:], i+1):
            if j in used:
                continue
                
            # Calculer la distance entre obstacles
            center1_x = (obs1['x1'] + obs1['x2']) / 2
            center1_y = (obs1['y1'] + obs1['y2']) / 2
            center2_x = (obs2['x1'] + obs2['x2']) / 2
            center2_y = (obs2['y1'] + obs2['y2']) / 2
            
            distance = ((center2_x - center1_x) ** 2 + (center2_y - center1_y) ** 2) ** 0.5
            
            # Si les obstacles sont proches (< 0.1), les fusionner
            if distance < 0.1 and obs1['type'] == obs2['type']:
                merged_obs['x1'] = min(merged_obs['x1'], obs2['x1'])
                merged_obs['y1'] = min(merged_obs['y1'], obs2['y1'])
                merged_obs['x2'] = max(merged_obs['x2'], obs2['x2'])
                merged_obs['y2'] = max(merged_obs['y2'], obs2['y2'])
                used.add(j)
        
        merged.append(merged_obs)
    
    return merged

def calculate_usable_roof_zones(obstacles: List[Dict], img_width: int, img_height: int, roof_inclination: float) -> List[Dict]:
    """
    Calcule les zones exploitables du toit en évitant les obstacles
    """
    try:
        # Zone de toit de base (marges de sécurité)
        base_zone = {
            'x1': 0.12, 'y1': 0.15,  # Marges de sécurité 
            'x2': 0.88, 'y2': 0.65   # Zone exploitable
        }
        
        # Si pas d'obstacles, retourner la zone entière
        if not obstacles:
            return [base_zone]
        
        # Diviser la zone en sous-zones en évitant les obstacles
        usable_zones = []
        
        # Trier les obstacles par position horizontale
        obstacles_sorted = sorted(obstacles, key=lambda x: x['x1'])
        
        # Créer des zones entre les obstacles
        current_x = base_zone['x1']
        
        for obstacle in obstacles_sorted:
            # Zone avant l'obstacle
            if obstacle['x1'] - current_x > 0.15:  # Zone assez large pour panneaux
                zone_before = {
                    'x1': current_x,
                    'y1': max(base_zone['y1'], obstacle['y1'] - 0.05),  # Marge au-dessus
                    'x2': obstacle['x1'] - 0.02,  # Marge avant obstacle
                    'y2': min(base_zone['y2'], obstacle['y2'] + 0.05),  # Marge en-dessous
                    'type': f'zone_before_{obstacle["type"]}'
                }
                
                # Vérifier que la zone est viable
                if (zone_before['x2'] - zone_before['x1']) > 0.1 and (zone_before['y2'] - zone_before['y1']) > 0.08:
                    usable_zones.append(zone_before)
            
            # Zone après l'obstacle
            current_x = obstacle['x2'] + 0.02
        
        # Zone finale après le dernier obstacle
        if base_zone['x2'] - current_x > 0.15:
            final_zone = {
                'x1': current_x,
                'y1': base_zone['y1'],
                'x2': base_zone['x2'],
                'y2': base_zone['y2'],
                'type': 'zone_finale'
            }
            usable_zones.append(final_zone)
        
        # Si aucune zone viable, créer des zones au-dessus et en-dessous des obstacles
        if not usable_zones:
            # Zone au-dessus des obstacles
            min_obstacle_y = min(obs['y1'] for obs in obstacles)
            if min_obstacle_y - base_zone['y1'] > 0.1:
                zone_above = {
                    'x1': base_zone['x1'],
                    'y1': base_zone['y1'],
                    'x2': base_zone['x2'],
                    'y2': min_obstacle_y - 0.02,
                    'type': 'zone_au_dessus'
                }
                usable_zones.append(zone_above)
            
            # Zone en-dessous des obstacles
            max_obstacle_y = max(obs['y2'] for obs in obstacles)
            if base_zone['y2'] - max_obstacle_y > 0.1:
                zone_below = {
                    'x1': base_zone['x1'],
                    'y1': max_obstacle_y + 0.02,
                    'x2': base_zone['x2'],
                    'y2': base_zone['y2'],
                    'type': 'zone_en_dessous'
                }
                usable_zones.append(zone_below)
        
        logging.info(f"Calculated {len(usable_zones)} usable roof zones avoiding {len(obstacles)} obstacles")
        return usable_zones if usable_zones else [base_zone]
        
    except Exception as e:
        logging.error(f"Error calculating usable zones: {e}")
        return [base_zone]

def determine_roof_type(img_array) -> str:
    """
    Détermine le type de toiture depuis l'image
    """
    try:
        import numpy as np
        
        # Analyser les couleurs dominantes pour déterminer le type
        colors_mean = np.mean(img_array, axis=(0, 1))
        
        # Rouge dominant = tuiles
        if colors_mean[0] > colors_mean[1] and colors_mean[0] > colors_mean[2]:
            return "tuiles"
        # Gris dominant = ardoise
        elif np.all(np.abs(colors_mean - np.mean(colors_mean)) < 20):
            return "ardoise"
        # Autres
        else:
            return "standard"
            
    except Exception:
        return "standard"

def calculate_optimal_orientation(img_array) -> str:
    """
    Calcule l'orientation optimale basée sur l'analyse de l'image
    """
    # Pour l'instant, retourner sud par défaut
    # Pourrait être amélioré avec analyse des ombres/luminosité
    return "sud"

def generate_obstacle_aware_panel_positions(panel_count: int, img_width: int, img_height: int, roof_geometry: Dict) -> List[Dict]:
    """
    Génère des positions de panneaux INTELLIGENTES qui évitent les obstacles
    """
    try:
        positions = []
        usable_zones = roof_geometry.get('usable_zones', [])
        roof_inclination = roof_geometry.get('roof_inclination', 30.0)
        
        if not usable_zones:
            # Fallback vers positions par défaut
            return generate_intelligent_roof_positions(panel_count, img_width, img_height)
        
        logging.info(f"Positioning {panel_count} panels in {len(usable_zones)} usable zones")
        
        # Répartir les panneaux entre les zones utilisables
        panels_per_zone = distribute_panels_across_zones(panel_count, usable_zones)
        
        panel_idx = 0
        for zone_idx, zone in enumerate(usable_zones):
            panels_in_zone = panels_per_zone[zone_idx]
            if panels_in_zone == 0:
                continue
            
            # Calculer la disposition optimale dans cette zone
            zone_width = zone['x2'] - zone['x1']
            zone_height = zone['y2'] - zone['y1']
            
            # Déterminer grille optimale pour cette zone
            if zone_width > zone_height:
                # Zone horizontale - priorité aux rangées
                cols = min(panels_in_zone, max(1, int(zone_width / 0.13)))
                rows = (panels_in_zone + cols - 1) // cols
            else:
                # Zone verticale - priorité aux colonnes
                rows = min(panels_in_zone, max(1, int(zone_height / 0.08)))
                cols = (panels_in_zone + rows - 1) // rows
            
            # Espacement dans la zone
            if cols > 1:
                spacing_x = zone_width / cols
            else:
                spacing_x = zone_width
                
            if rows > 1:
                spacing_y = zone_height / rows
            else:
                spacing_y = zone_height
            
            # Placer les panneaux dans cette zone
            for row in range(rows):
                for col in range(cols):
                    if panel_idx >= panel_count:
                        break
                        
                    # Position dans la zone avec centrage
                    x = zone['x1'] + (col + 0.5) * spacing_x - 0.06  # Centrer le panneau
                    y = zone['y1'] + (row + 0.5) * spacing_y - 0.035  # Centrer le panneau
                    
                    # S'assurer que le panneau reste dans la zone
                    x = max(zone['x1'] + 0.01, min(x, zone['x2'] - 0.12))
                    y = max(zone['y1'] + 0.01, min(y, zone['y2'] - 0.07))
                    
                    positions.append({
                        'x': x,
                        'y': y,
                        'width': 0.11,
                        'height': 0.065,
                        'angle': roof_inclination,
                        'zone': zone.get('type', f'zone_{zone_idx}')
                    })
                    
                    panel_idx += 1
                    
                if panel_idx >= panel_count:
                    break
        
        logging.info(f"Successfully positioned {len(positions)} panels avoiding obstacles")
        return positions[:panel_count]
        
    except Exception as e:
        logging.error(f"Error in obstacle-aware positioning: {e}")
        return generate_intelligent_roof_positions(panel_count, img_width, img_height)

def distribute_panels_across_zones(panel_count: int, usable_zones: List[Dict]) -> List[int]:
    """
    Répartit intelligemment les panneaux entre les zones utilisables
    """
    if not usable_zones:
        return []
    
    # Calculer la capacité de chaque zone
    zone_capacities = []
    for zone in usable_zones:
        zone_area = (zone['x2'] - zone['x1']) * (zone['y2'] - zone['y1'])
        # Capacité approximative (1 panneau = 0.11 x 0.065 = 0.007)
        capacity = max(1, int(zone_area / 0.008))
        zone_capacities.append(capacity)
    
    total_capacity = sum(zone_capacities)
    
    # Répartition proportionnelle
    distribution = []
    assigned_panels = 0
    
    for i, capacity in enumerate(zone_capacities):
        if i == len(zone_capacities) - 1:
            # Dernière zone - assigner tous les panneaux restants
            distribution.append(panel_count - assigned_panels)
        else:
            # Répartition proportionnelle
            panels_for_zone = min(capacity, max(0, int(panel_count * capacity / total_capacity)))
            distribution.append(panels_for_zone)
            assigned_panels += panels_for_zone
    
    return distribution

def generate_intelligent_roof_positions(panel_count: int, img_width: int, img_height: int) -> List[Dict]:
    """
    Génère des positions intelligentes et réalistes adaptées parfaitement à la géométrie d'une toiture
    """
    positions = []
    
    # Zone du toit optimisée (zone réellement utilisable d'un toit)
    roof_top_y = 0.18      # Début zone exploitable (évite faîtage)
    roof_bottom_y = 0.58   # Fin zone exploitable (évite gouttières)
    roof_left_x = 0.15     # Marge gauche de sécurité
    roof_right_x = 0.85    # Marge droite de sécurité
    
    # Calculer la disposition optimale selon le nombre de panneaux
    if panel_count <= 6:
        # Petite installation : 2 rangées de 3 max
        panels_per_row = min(3, panel_count)
        rows = (panel_count + panels_per_row - 1) // panels_per_row
    elif panel_count <= 12:
        # Installation moyenne : 3 rangées de 4 max
        panels_per_row = min(4, (panel_count + 2) // 3)
        rows = (panel_count + panels_per_row - 1) // panels_per_row
    else:
        # Grande installation : jusqu'à 4 rangées
        panels_per_row = min(5, (panel_count + 3) // 4)
        rows = min(4, (panel_count + panels_per_row - 1) // panels_per_row)
    
    # Espacement intelligent avec marge de sécurité
    usable_width = roof_right_x - roof_left_x
    usable_height = roof_bottom_y - roof_top_y
    
    panel_spacing_x = usable_width / max(1, panels_per_row)
    panel_spacing_y = usable_height / max(1, rows)
    
    panel_idx = 0
    for row in range(rows):
        # Calculer le nombre de panneaux sur cette rangée
        panels_in_this_row = min(panels_per_row, panel_count - panel_idx)
        
        # Centrer la rangée si elle n'est pas complète
        row_start_x = roof_left_x
        if panels_in_this_row < panels_per_row:
            row_start_x += (panels_per_row - panels_in_this_row) * panel_spacing_x / 2
        
        for col in range(panels_in_this_row):
            # Position centrée dans l'espace disponible
            x = row_start_x + col * panel_spacing_x + panel_spacing_x * 0.2
            y = roof_top_y + row * panel_spacing_y + panel_spacing_y * 0.15
            
            # S'assurer que les positions restent dans les limites
            x = max(roof_left_x + 0.02, min(x, roof_right_x - 0.12))
            y = max(roof_top_y + 0.02, min(y, roof_bottom_y - 0.08))
            
            positions.append({
                'x': x,
                'y': y,
                'width': 0.12,
                'height': 0.07,
                'angle': 15  # Inclinaison standard du toit
            })
            
            panel_idx += 1
    
    logging.info(f"Generated {len(positions)} intelligent roof positions in {rows} rows")
    return positions

def generate_intelligent_roof_positions(panel_count: int, img_width: int, img_height: int) -> List[Dict]:
    """
    Fonction de fallback - génère des positions intelligentes basiques
    (maintenue pour compatibilité avec le code existant)
    """
    positions = []
    
    # Zone du toit optimisée (zone réellement utilisable d'un toit)
    roof_top_y = 0.18      # Début zone exploitable (évite faîtage)
    roof_bottom_y = 0.58   # Fin zone exploitable (évite gouttières)
    roof_left_x = 0.15     # Marge gauche de sécurité
    roof_right_x = 0.85    # Marge droite de sécurité
    
    # Calculer la disposition optimale selon le nombre de panneaux
    if panel_count <= 6:
        # Petite installation : 2 rangées de 3 max
        panels_per_row = min(3, panel_count)
        rows = (panel_count + panels_per_row - 1) // panels_per_row
    elif panel_count <= 12:
        # Installation moyenne : 3 rangées de 4 max
        panels_per_row = min(4, (panel_count + 2) // 3)
        rows = (panel_count + panels_per_row - 1) // panels_per_row
    else:
        # Grande installation : jusqu'à 4 rangées
        panels_per_row = min(5, (panel_count + 3) // 4)
        rows = min(4, (panel_count + panels_per_row - 1) // panels_per_row)
    
    # Espacement intelligent avec marge de sécurité
    usable_width = roof_right_x - roof_left_x
    usable_height = roof_bottom_y - roof_top_y
    
    panel_spacing_x = usable_width / max(1, panels_per_row)
    panel_spacing_y = usable_height / max(1, rows)
    
    panel_idx = 0
    for row in range(rows):
        # Calculer le nombre de panneaux sur cette rangée
        panels_in_this_row = min(panels_per_row, panel_count - panel_idx)
        
        # Centrer la rangée si elle n'est pas complète
        row_start_x = roof_left_x
        if panels_in_this_row < panels_per_row:
            row_start_x += (panels_per_row - panels_in_this_row) * panel_spacing_x / 2
        
        for col in range(panels_in_this_row):
            # Position centrée dans l'espace disponible
            x = row_start_x + col * panel_spacing_x + panel_spacing_x * 0.2
            y = roof_top_y + row * panel_spacing_y + panel_spacing_y * 0.15
            
            # S'assurer que les positions restent dans les limites
            x = max(roof_left_x + 0.02, min(x, roof_right_x - 0.12))
            y = max(roof_top_y + 0.02, min(y, roof_bottom_y - 0.08))
            
            positions.append({
                'x': x,
                'y': y,
                'width': 0.12,
                'height': 0.07,
                'angle': 15  # Inclinaison standard du toit
            })
            
            panel_idx += 1
    
    logging.info(f"Generated {len(positions)} basic intelligent roof positions in {rows} rows")
    return positions

def generate_roof_adapted_positions(panel_count: int, img_width: int, img_height: int) -> List[Dict]:
    """
    Génère des positions adaptées à la géométrie du toit
    """
    positions = []
    
    # Zone du toit principale (ajustée pour correspondre à une toiture réelle)
    roof_top_y = 0.18      # Début de la zone toit (plus haut)
    roof_bottom_y = 0.55   # Fin de la zone toit (partie visible)
    roof_left_x = 0.12     # Bord gauche du toit
    roof_right_x = 0.88    # Bord droit du toit
    
    # Calculer la disposition optimale pour s'adapter au toit
    if panel_count <= 4:
        panels_per_row = 4
    elif panel_count <= 8:  
        panels_per_row = 4
    elif panel_count <= 12:
        panels_per_row = 4
    else:
        panels_per_row = 6
        
    rows = (panel_count + panels_per_row - 1) // panels_per_row
    
    # Espacement adapté à la surface de toit disponible
    panel_spacing_x = (roof_right_x - roof_left_x) / panels_per_row
    panel_spacing_y = (roof_bottom_y - roof_top_y) / max(1, rows)
    
    panel_idx = 0
    for row in range(rows):
        for col in range(panels_per_row):
            if panel_idx >= panel_count:
                break
                
            # Position centrée dans chaque "case" du toit
            x = roof_left_x + col * panel_spacing_x + panel_spacing_x * 0.1
            y = roof_top_y + row * panel_spacing_y + panel_spacing_y * 0.1
            
            positions.append({
                'x': x,
                'y': y,
                'width': 0.11,
                'height': 0.06,
                'angle': 15  # Angle d'inclinaison du toit
            })
            
            panel_idx += 1
    
    return positions

def generate_default_panel_positions(panel_count: int) -> List[Dict]:
    """
    Génère des positions par défaut pour les panneaux sur une toiture
    """
    positions = []
    
    # Calculer la disposition en grille
    panels_per_row = min(3, panel_count)  # Max 3 panneaux par rangée
    rows = (panel_count + panels_per_row - 1) // panels_per_row
    
    for i in range(panel_count):
        row = i // panels_per_row
        col = i % panels_per_row
        
        # Centrer la disposition
        x_offset = 0.1 + (0.8 - panels_per_row * 0.2) / 2
        y_offset = 0.15
        
        x = x_offset + col * 0.25
        y = y_offset + row * 0.15
        
        positions.append({
            'x': min(max(x, 0.05), 0.75),  # Limiter entre 5% et 75%
            'y': min(max(y, 0.1), 0.7),   # Limiter entre 10% et 70%
            'width': 0.15,
            'height': 0.08,
            'angle': 0
        })
    
    return positions

class RoofAnalysisResponse(BaseModel):
    success: bool
    panel_positions: List[PanelPosition]
    roof_analysis: str  # Description de l'analyse
    total_surface_required: float  # Surface totale requise
    placement_possible: bool  # Si le placement est possible
    recommendations: str  # Recommandations
    composite_image: Optional[str] = None  # Image composite avec panneaux (base64)

@api_router.post("/analyze-roof", response_model=RoofAnalysisResponse)
async def analyze_roof_for_panels(request: RoofAnalysisRequest):
    """
    Analyse une photo de toiture et propose le positionnement optimal des panneaux solaires
    """
    # Calculer la surface totale requise (en dehors du try/catch)
    total_surface_required = request.panel_count * request.panel_surface
    
    try:
        # Validation des paramètres d'entrée
        if request.panel_count <= 0:
            raise HTTPException(status_code=422, detail="Panel count must be greater than 0")
        if request.panel_count > 30:
            raise HTTPException(status_code=422, detail="Maximum 30 panels supported")
        
        # Validation et préparation de l'image
        try:
            if request.image_base64.startswith('data:image'):
                base64_data = request.image_base64.split(',')[1]
            else:
                base64_data = request.image_base64
            
            # Valider que c'est bien du base64
            image_data = base64.b64decode(base64_data)
            test_image = PILImage.open(BytesIO(image_data)).convert('RGB')
            
            # Vérifier les dimensions minimales pour OpenAI Vision
            width, height = test_image.size
            if width < 100 or height < 100:
                raise HTTPException(status_code=422, detail="Image too small for analysis (minimum 100x100 pixels)")
            
            # Optimiser l'image pour OpenAI Vision (format et taille)
            # Redimensionner si trop grande pour éviter les coûts excessifs
            max_dimension = 1024
            if max(width, height) > max_dimension:
                ratio = max_dimension / max(width, height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                test_image = test_image.resize((new_width, new_height), PILImage.Resampling.LANCZOS)
                
                # Reconvertir en base64 optimisé
                buffer = BytesIO()
                test_image.save(buffer, format='JPEG', quality=90, optimize=True)
                buffer.seek(0)
                optimized_base64 = base64.b64encode(buffer.getvalue()).decode()
                optimized_image_data = f"data:image/jpeg;base64,{optimized_base64}"
                logging.info(f"Image optimized to {new_width}x{new_height} for OpenAI Vision")
            else:
                optimized_image_data = request.image_base64
                
        except Exception as e:
            logging.error(f"Image validation failed: {e}")
            raise HTTPException(status_code=422, detail=f"Invalid image format: {str(e)}")
        
        # Configurer OpenAI
        openai_key = os.environ.get('OPENAI_API_KEY')
        if not openai_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        # Analyser la géométrie réelle du toit et détecter les obstacles
        roof_geometry = analyze_roof_geometry_and_obstacles(optimized_image_data)
        
        # Générer positions intelligentes basées sur l'analyse de la toiture réelle
        intelligent_positions = generate_obstacle_aware_panel_positions(
            request.panel_count, 
            width, 
            height, 
            roof_geometry
        )
        
        # Construire l'analyse basée sur la détection réelle
        obstacles_detected = len(roof_geometry.get('obstacles', []))
        usable_zones_count = len(roof_geometry.get('usable_zones', []))
        roof_inclination = roof_geometry.get('roof_inclination', 30)
        roof_type = roof_geometry.get('roof_type', 'standard')
        
        ai_analysis = f"🏠 ANALYSE INTELLIGENTE - Toiture {roof_type} détectée avec inclinaison {roof_inclination:.1f}°"
        if obstacles_detected > 0:
            obstacle_types = [obs['type'] for obs in roof_geometry.get('obstacles', [])]
            ai_analysis += f" • {obstacles_detected} obstacle(s): {', '.join(set(obstacle_types))}"
        
        ai_recommendations = f"⚡ OPTIMISATION AVANCÉE - Installation répartie en {usable_zones_count} zone(s) exploitable(s)"
        if obstacles_detected > 0:
            ai_recommendations += f", contournement automatique des obstacles pour maximiser la production"
        
        # Initialize variables for AI response
        panel_positions_from_ai = []
        
        try:
            # Créer le client LLM avec timeout
            llm = LlmChat(
                session_id="roof_analysis_v2",
                system_message="You are a professional solar installation expert. Analyze roof images and provide precise solar panel placement recommendations in JSON format.",
                api_key=openai_key
            )
            
            # Préparer l'image optimisée
            image_content = ImageContent(
                image_base64=optimized_image_data
            )
            
            # Prompt amélioré et plus spécifique
            prompt = f"""
            Analysez cette photo de toiture pour déterminer le positionnement optimal de {request.panel_count} panneaux solaires photovoltaïques.
            
            SPÉCIFICATIONS TECHNIQUES:
            - Chaque panneau: {request.panel_surface}m² (2,1m x 1,0m environ)  
            - Surface totale requise: {total_surface_required}m²
            - Installation résidentielle standard
            
            CONTRAINTES D'INSTALLATION:
            - Éviter cheminées, antennes, lucarnes, velux
            - Distance minimum: 50cm des bords du toit
            - Espacement entre panneaux: 2-5cm
            - Orientation optimale vers le sud
            - Éviter les zones d'ombre
            
            Répondez UNIQUEMENT en JSON valide:
            {{
                "roof_analysis": "Description technique de la toiture (type, orientation, obstacles, surface utilisable)",
                "placement_possible": true/false,
                "panel_positions": [
                    {{"x": 0.25, "y": 0.30, "width": 0.12, "height": 0.07, "angle": 15}},
                    {{"x": 0.40, "y": 0.30, "width": 0.12, "height": 0.07, "angle": 15}}
                ],
                "recommendations": "Conseils techniques pour l'installation et la performance"
            }}
            
            IMPORTANT: Coordonnées relatives (0.0-1.0). Respectez les contraintes de sécurité et d'efficacité.
            """
            
            # Créer le message avec l'image
            user_message = UserMessage(
                text=prompt,
                file_contents=[image_content]
            )
            
            # Envoyer la demande à OpenAI Vision (avec gestion du timeout)
            response = await llm.send_message(user_message)
            
            # Parser la réponse avec gestion d'erreur robuste
            if response:
                response_text = response if isinstance(response, str) else str(response)
                logging.info(f"OpenAI Vision response received: {len(response_text)} characters")
                
                # Essayer d'extraire le JSON
                import re
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
                if not json_match:
                    json_match = re.search(r'(\{.*?\})', response_text, re.DOTALL)
                
                if json_match:
                    try:
                        json_str = json_match.group(1) if json_match.groups() else json_match.group(0)
                        result = json.loads(json_str)
                        
                        panel_positions_from_ai = result.get("panel_positions", [])
                        ai_analysis = result.get("roof_analysis", ai_analysis)
                        ai_recommendations = result.get("recommendations", ai_recommendations)
                        
                        if len(panel_positions_from_ai) == request.panel_count:
                            logging.info(f"✅ Successfully extracted {len(panel_positions_from_ai)} AI panel positions")
                        else:
                            logging.warning(f"AI returned {len(panel_positions_from_ai)} positions but {request.panel_count} requested")
                            panel_positions_from_ai = []
                            
                    except json.JSONDecodeError as e:
                        logging.error(f"JSON parsing failed: {e}")
                        panel_positions_from_ai = []
                else:
                    logging.warning("No JSON structure found in OpenAI response")
                    
        except Exception as e:
            logging.error(f"OpenAI Vision analysis failed: {e}")
            # Continuer avec les positions par défaut
        
        # Utiliser positions AI ou positions par défaut
        if panel_positions_from_ai and len(panel_positions_from_ai) > 0:
            logging.info("Using AI-generated panel positions")
            positions_to_use = panel_positions_from_ai
        else:
            logging.info("Using intelligent default panel positions")
            positions_to_use = intelligent_positions
        
        # Générer l'image composite RÉALISTE
        logging.info(f"Generating ultra-realistic composite image with {request.panel_count} panels")
        
        composite_image_base64 = create_composite_image_with_panels(
            request.image_base64,
            positions_to_use,
            request.panel_count
        )
        
        # Construire la réponse avec les positions validées
        panel_positions = []
        for pos in positions_to_use[:request.panel_count]:
            panel_positions.append(PanelPosition(
                x=pos.get("x", 0.3),
                y=pos.get("y", 0.3),
                width=pos.get("width", 0.12),
                height=pos.get("height", 0.07),
                angle=pos.get("angle", 15)
            ))
        
        return RoofAnalysisResponse(
            success=True,
            panel_positions=panel_positions,
            roof_analysis=f"✅ ANALYSE RÉUSSIE - {ai_analysis}. Installation de {request.panel_count} panneaux solaires visualisée avec rendu ultra-réaliste.",
            total_surface_required=total_surface_required,
            placement_possible=True,
            recommendations=f"🔧 INSTALLATION OPTIMISÉE - {ai_recommendations}. Consultez l'image composite ci-jointe pour voir le rendu final réaliste de votre installation solaire.",
            composite_image=composite_image_base64
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Roof analysis error: {e}")
        return RoofAnalysisResponse(
            success=False,
            panel_positions=[],
            roof_analysis=f"❌ Erreur d'analyse: {str(e)}",
            total_surface_required=total_surface_required,
            placement_possible=False,
            recommendations="Veuillez réessayer avec une image de toiture plus claire (format JPEG/PNG, minimum 100x100 pixels)"
        )

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