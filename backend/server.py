from fastapi import FastAPI, APIRouter, HTTPException, Response, UploadFile, File, Form
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
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
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
from pypdf import PdfReader, PdfWriter

# OpenAI Vision imports - Updated LLMChat to LlmChat
from emergentintegrations.llm.chat import ImageContent, UserMessage, LlmChat

# fal.ai client for solar panel visualization
import fal_client

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
                "panels": 8,
                "price_ttc": 10900,
                "aid_amount": 5340,
                "surface": 16.8,  # m² calculée (8 × 2.1)
                "description": "Kit 3kW - Résidentiel"
            },
            "kit_6kw": {
                "power": 6,
                "panels": 16,
                "price_ttc": 15900,
                "aid_amount": 6480,
                "surface": 33.6,  # m² calculée (16 × 2.1)
                "description": "Kit 6kW - Résidentiel+"
            },
            "kit_9kw": {
                "power": 9,
                "panels": 24,
                "price_ttc": 18900,
                "aid_amount": 9720,
                "surface": 50.4,  # m² calculée (24 × 2.1)
                "description": "Kit 9kW - Grande résidence"
            },
            "kit_12kw": {
                "power": 12,
                "panels": 32,
                "price_ttc": 22900,
                "aid_amount": 9720,
                "surface": 67.2,  # m² calculée (32 × 2.1)
                "description": "Kit 12kW - Résidentiel large"
            },
            "kit_15kw": {
                "power": 15,
                "panels": 40,
                "price_ttc": 25900,
                "aid_amount": 12150,
                "surface": 84.0,  # m² calculée (40 × 2.1)
                "description": "Kit 15kW - Commercial petit"
            },
            "kit_18kw": {
                "power": 18,
                "panels": 48,
                "price_ttc": 28900,
                "aid_amount": 14580,
                "surface": 100.8,  # m² calculée (48 × 2.1)
                "description": "Kit 18kW - Commercial moyen"
            },
            "kit_21kw": {
                "power": 21,
                "panels": 56,
                "price_ttc": 30900,
                "aid_amount": 17010,
                "surface": 117.6,  # m² calculée (56 × 2.1)
                "description": "Kit 21kW - Commercial+"
            },
            "kit_24kw": {
                "power": 24,
                "panels": 64,
                "price_ttc": 32900,
                "aid_amount": 19440,
                "surface": 134.4,  # m² calculée (64 × 2.1)
                "description": "Kit 24kW - Commercial large"
            },
            "kit_27kw": {
                "power": 27,
                "panels": 72,
                "price_ttc": 34900,
                "aid_amount": 21870,
                "surface": 151.2,  # m² calculée (72 × 2.1)
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

# Roof Visualization Models
class RoofVisualizationRequest(BaseModel):
    image_data: str  # base64 encoded image
    kit_power: int  # Selected kit power (3, 6, 9, etc.)
    region: str = "france"  # france or martinique

class RoofVisualizationResponse(BaseModel):
    success: bool
    generated_image_url: Optional[str] = None
    original_image_data: Optional[str] = None
    kit_info: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

class ImageUploadResponse(BaseModel):
    success: bool
    image_data: Optional[str] = None  # base64 encoded
    file_size: Optional[int] = None
    error_message: Optional[str] = None

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

def calculate_financing_options(kit_price: float, monthly_savings: float, region: str = "france", discount_amount: float = 0, battery_cost: float = 0) -> List[Dict]:
    """
    Calculate financing options from 3 to 15 years based on region
    """
    region_config = REGIONS_CONFIG.get(region, REGIONS_CONFIG["france"])
    taeg = region_config["interest_rates"]["standard"]
    monthly_rate = taeg / 12
    
    # Appliquer la remise et ajouter le coût batterie si fourni
    final_price = kit_price - discount_amount + battery_cost
    
    min_duration = region_config["financing"]["min_duration"]
    max_duration = region_config["financing"]["max_duration"]
    
    options = []
    
    for years in range(min_duration, max_duration + 1):
        months = years * 12
        
        if monthly_rate > 0:
            # Standard loan calculation with discounted price
            monthly_payment = final_price * (monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)
        else:
            monthly_payment = final_price / months
        
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

def calculate_financing_with_aids(kit_price: float, total_aids: float, monthly_savings: float, region: str = "france", financing_options: List[Dict] = None, discount_amount: float = 0, battery_cost: float = 0) -> Dict:
    """
    Calculate financing options with aids deducted - WITH INTERESTS
    """
    region_config = REGIONS_CONFIG.get(region, REGIONS_CONFIG["france"])
    taeg = region_config["interest_rates"]["with_aids"]
    
    # Calculer le prix final avec remise et batterie, puis retirer les aides
    final_price_before_aids = kit_price - discount_amount + battery_cost
    financed_amount = final_price_before_aids - total_aids
    
    if financed_amount <= 0:
        return {
            "monthly_payment": 0,
            "financed_amount": 0,
            "duration_years": 0,
            "duration_months": 0,
            "difference_vs_savings": round(-monthly_savings, 2)
        }
    
    # Get financing options to determine optimal duration
    if financing_options is None:
        financing_options = calculate_financing_options(kit_price, monthly_savings, region, discount_amount, battery_cost)
    
    # Find optimal financing duration based on the same logic as frontend
    optimal_duration = find_optimal_duration(financing_options, monthly_savings)
    
    # Calculate monthly payment with interest
    monthly_rate = taeg / 12
    months = optimal_duration * 12
    
    if monthly_rate > 0:
        monthly_payment = financed_amount * (monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)
    else:
        monthly_payment = financed_amount / months
        
    return {
        "monthly_payment": round(monthly_payment, 2),
        "financed_amount": round(financed_amount, 2),
        "duration_years": optimal_duration,
        "duration_months": months,
        "difference_vs_savings": round(monthly_payment - monthly_savings, 2)
    }

def calculate_all_financing_with_aids(kit_price: float, total_aids: float, monthly_savings: float, region: str = "france", discount_amount: float = 0, battery_cost: float = 0) -> List[Dict]:
    """
    Calculate financing options with aids deducted for all durations (3-15 years) - WITH INTERESTS
    """
    region_config = REGIONS_CONFIG.get(region, REGIONS_CONFIG["france"])
    taeg = region_config["interest_rates"]["with_aids"]
    monthly_rate = taeg / 12
    
    min_duration = region_config["financing"]["min_duration"]
    max_duration = region_config["financing"]["max_duration"]
    
    # Calculer le prix final avec remise et batterie, puis retirer les aides
    final_price_before_aids = kit_price - discount_amount + battery_cost
    financed_amount = final_price_before_aids - total_aids
    
    options = []
    
    for years in range(min_duration, max_duration + 1):
        months = years * 12
        
        if monthly_rate > 0:
            # Standard loan calculation
            monthly_payment = financed_amount * (monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)
        else:
            monthly_payment = financed_amount / months
        
        # Calculate total cost and interests
        total_cost = monthly_payment * months
        total_interests = total_cost - financed_amount
        
        options.append({
            "duration_years": years,
            "duration_months": months,
            "monthly_payment": round(monthly_payment, 2),
            "total_cost": round(total_cost, 2),
            "total_interests": round(total_interests, 2),
            "amount_financed": round(financed_amount, 2),
            "taeg": taeg,
            "difference_vs_savings": round(monthly_payment - monthly_savings, 2)
        })
    
    return options

# =============================================================================
# ROOF VISUALIZATION FUNCTIONS WITH FAL.AI
# =============================================================================

def get_panel_count_by_kit_power(kit_power: int, region: str = "france") -> int:
    """Get number of panels based on kit power and region"""
    if region == "martinique":
        region_kits = REGIONS_CONFIG["martinique"]["kits"]
        for kit_id, kit_data in region_kits.items():
            if kit_data["power"] == kit_power:
                return kit_data["panels"]
        return kit_power * 2.67  # Fallback calculation
    else:
        return SOLAR_KITS.get(kit_power, {}).get("panels", kit_power * 2)

async def generate_solar_panel_visualization(image_data: str, kit_power: int, region: str = "france") -> Dict[str, Any]:
    """
    Generate solar panel visualization by overlaying realistic panels directly on the original image
    
    Args:
        image_data: Base64 encoded image data
        kit_power: Power of the selected kit (3, 6, 9, etc.)
        region: Region (france or martinique)
    
    Returns:
        Dict with success status and generated image URL or error message
    """
    try:
        # Get panel count for the kit
        panel_count = get_panel_count_by_kit_power(kit_power, region)
        
        # Decode the base64 image
        if image_data.startswith('data:image'):
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        original_image = PILImage.open(BytesIO(image_bytes))
        
        # Convert to RGB if needed
        if original_image.mode != 'RGB':
            original_image = original_image.convert('RGB')
        
        # Create modified image with solar panels
        modified_image = add_solar_panels_to_roof(original_image, panel_count)
        
        # Convert back to base64
        buffer = BytesIO()
        modified_image.save(buffer, format='JPEG', quality=90)
        buffer.seek(0)
        
        result_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        result_data_url = f"data:image/jpeg;base64,{result_base64}"
        
        return {
            "success": True,
            "generated_image_url": result_data_url,
            "panel_count": panel_count,
            "kit_power": kit_power
        }
        
    except Exception as e:
        logging.error(f"Error generating solar visualization: {str(e)}")
        return {
            "success": False,
            "error_message": f"Generation error: {str(e)}"
        }

def add_solar_panels_to_roof(image: PILImage.Image, panel_count: int) -> PILImage.Image:
    """
    Add solar panels with TRUE roof slope perspective creating pronounced parallelograms
    Matching exactly the reference installation photos with correct left/right incline
    
    Args:
        image: Original PIL Image
        panel_count: Number of panels to add
    
    Returns:
        Modified PIL Image with properly inclined parallelogram solar panels
    """
    try:
        # Work with a copy of the original image
        result_image = image.copy()
        width, height = result_image.size
        draw = ImageDraw.Draw(result_image)
        
        # REAL SOLAR PANEL DIMENSIONS: 1.71m x 1.10m
        real_panel_ratio = 1.71 / 1.10  # = 1.55:1
        
        # ULTRA CONSERVATIVE roof area to prevent ANY spillover
        roof_start_y = int(height * 0.18)   # Sky margin
        roof_end_y = int(height * 0.48)     # Big bottom margin  
        roof_start_x = int(width * 0.26)    # Big left margin
        roof_end_x = int(width * 0.74)      # Big right margin
        
        roof_width = roof_end_x - roof_start_x
        roof_height = roof_end_y - roof_start_y
        
        # Layout for 16 panels - use 4x4 for better control
        cols, rows = 4, 4
        
        # Calculate panel size (more conservative to prevent spillover)
        base_panel_width = int(roof_width / cols * 0.80)  # 80% utilization
        base_panel_height = int(base_panel_width * real_panel_ratio)
        
        # Ensure panels fit with generous spacing
        spacing_x = max(10, (roof_width - cols * base_panel_width) // (cols + 1))
        spacing_y = max(10, (roof_height - rows * base_panel_height) // (rows + 1))
        
        # Final safety check - scale down if needed
        total_width = cols * base_panel_width + (cols - 1) * spacing_x
        total_height = rows * base_panel_height + (rows - 1) * spacing_y
        
        if total_width > roof_width * 0.85 or total_height > roof_height * 0.85:
            scale = min(roof_width * 0.85 / total_width, roof_height * 0.85 / total_height)
            base_panel_width = int(base_panel_width * scale)
            base_panel_height = int(base_panel_height * scale)
            spacing_x = int(spacing_x * scale)
            spacing_y = int(spacing_y * scale)
            
        # Recalculate final dimensions
        final_total_width = cols * base_panel_width + (cols - 1) * spacing_x
        final_total_height = rows * base_panel_height + (rows - 1) * spacing_y
        
        # Centered starting position
        start_x = roof_start_x + (roof_width - final_total_width) // 2
        start_y = roof_start_y + (roof_height - final_total_height) // 2
        
        # CRITICAL: Create PRONOUNCED parallelogram effect like in reference photos
        # Your reference photos show very strong perspective distortion
        roof_slope_shift = int(base_panel_width * 0.35)  # 35% slope shift (very pronounced)
        
        panels_placed = 0
        
        for row in range(rows):
            if panels_placed >= panel_count:
                break
                
            for col in range(cols):
                if panels_placed >= panel_count:
                    break
                
                # Base position
                base_x = start_x + col * (base_panel_width + spacing_x)
                base_y = start_y + row * (base_panel_height + spacing_y)
                
                # CREATE PRONOUNCED PARALLELOGRAM following roof slope
                # Key insight from your reference photos: very strong left-right perspective
                
                # Panel corners as pronounced parallelogram
                # Top edge shifts significantly left (following roof incline)
                top_left_x = base_x - roof_slope_shift
                top_left_y = base_y
                top_right_x = base_x + base_panel_width - roof_slope_shift
                top_right_y = base_y
                
                # Bottom edge remains normal
                bottom_left_x = base_x
                bottom_left_y = base_y + base_panel_height
                bottom_right_x = base_x + base_panel_width
                bottom_right_y = base_y + base_panel_height
                
                # STEP 1: Draw pronounced shadow (parallelogram shape)
                shadow_offset = 6
                shadow_points = [
                    (top_left_x + shadow_offset, top_left_y + shadow_offset),
                    (top_right_x + shadow_offset, top_right_y + shadow_offset),
                    (bottom_right_x + shadow_offset, bottom_right_y + shadow_offset),
                    (bottom_left_x + shadow_offset, bottom_left_y + shadow_offset)
                ]
                
                overlay = PILImage.new('RGBA', (width, height), (0, 0, 0, 0))
                overlay_draw = ImageDraw.Draw(overlay)
                overlay_draw.polygon(shadow_points, fill=(0, 0, 0, 70))
                result_image = PILImage.alpha_composite(result_image.convert('RGBA'), overlay).convert('RGB')
                draw = ImageDraw.Draw(result_image)
                
                # STEP 2: Draw 3D depth faces (pronounced like reference photos)
                depth = 10  # More pronounced 3D effect
                
                # Right side face (very visible due to strong perspective)
                right_face_points = [
                    (top_right_x, top_right_y),
                    (top_right_x + depth, top_right_y - depth),
                    (bottom_right_x + depth, bottom_right_y - depth),
                    (bottom_right_x, bottom_right_y)
                ]
                draw.polygon(right_face_points, fill=(4, 10, 18))  # Dark side
                
                # Bottom side face (darker for strong depth)
                bottom_face_points = [
                    (bottom_left_x, bottom_left_y),
                    (bottom_right_x, bottom_right_y),
                    (bottom_right_x + depth, bottom_right_y - depth),
                    (bottom_left_x + depth, bottom_left_y - depth)
                ]
                draw.polygon(bottom_face_points, fill=(2, 6, 12))  # Darker bottom
                
                # STEP 3: Draw thick aluminum frame (parallelogram)
                frame_thickness = 5
                frame_points = [
                    (top_left_x - frame_thickness, top_left_y - frame_thickness),
                    (top_right_x + frame_thickness, top_right_y - frame_thickness),
                    (bottom_right_x + frame_thickness, bottom_right_y + frame_thickness),
                    (bottom_left_x - frame_thickness, bottom_left_y + frame_thickness)
                ]
                draw.polygon(frame_points, fill=(150, 150, 155))  # Aluminum
                
                # STEP 4: Draw main panel (PRONOUNCED PARALLELOGRAM)
                panel_points = [
                    (top_left_x, top_left_y),
                    (top_right_x, top_right_y),
                    (bottom_right_x, bottom_right_y),
                    (bottom_left_x, bottom_left_y)
                ]
                draw.polygon(panel_points, fill=(15, 25, 40))  # Dark blue/black
                
                # STEP 5: Solar cell grid (following pronounced parallelogram)
                cells_x, cells_y = 6, 10
                grid_color = (25, 35, 50)
                
                # Vertical lines (following strong slope distortion)
                for i in range(1, cells_x):
                    ratio = i / cells_x
                    line_top_x = int(top_left_x + ratio * (top_right_x - top_left_x))
                    line_bottom_x = int(bottom_left_x + ratio * (bottom_right_x - bottom_left_x))
                    draw.line([line_top_x, top_left_y, line_bottom_x, bottom_left_y], 
                             fill=grid_color, width=2)
                
                # Horizontal lines (parallel to parallelogram edges)
                for i in range(1, cells_y):
                    ratio = i / cells_y
                    # Left side of line (with slope)
                    line_left_x = int(top_left_x + ratio * (bottom_left_x - top_left_x))
                    line_left_y = int(top_left_y + ratio * (bottom_left_y - top_left_y))
                    # Right side of line (with slope)
                    line_right_x = int(top_right_x + ratio * (bottom_right_x - top_right_x))
                    line_right_y = int(top_right_y + ratio * (bottom_right_y - top_right_y))
                    draw.line([line_left_x, line_left_y, line_right_x, line_right_y], 
                             fill=grid_color, width=2)
                
                # STEP 6: Glass reflection (following pronounced slope)
                reflection_height = base_panel_height // 3
                reflection_points = [
                    (top_left_x, top_left_y),
                    (top_right_x, top_right_y),
                    (int(top_right_x + (bottom_right_x - top_right_x) * 0.35), 
                     int(top_right_y + reflection_height)),
                    (int(top_left_x + (bottom_left_x - top_left_x) * 0.35), 
                     int(top_left_y + reflection_height))
                ]
                
                reflection_overlay = PILImage.new('RGBA', (width, height), (0, 0, 0, 0))
                reflection_draw = ImageDraw.Draw(reflection_overlay)
                reflection_draw.polygon(reflection_points, fill=(60, 90, 130, 45))
                result_image = PILImage.alpha_composite(result_image.convert('RGBA'), reflection_overlay).convert('RGB')
                draw = ImageDraw.Draw(result_image)
                
                panels_placed += 1
        
        return result_image
        
    except Exception as e:
        logging.error(f"Error adding pronounced slope-following solar panels: {str(e)}")
        return image

def optimize_panel_layout(panel_count: int, available_width: int, available_height: int) -> Dict[str, int]:
    """
    Optimize panel layout to best fit the available roof space
    
    Args:
        panel_count: Number of panels to place
        available_width: Available width on roof
        available_height: Available height on roof
    
    Returns:
        Dict with optimal rows and cols
    """
    # Try different layout configurations
    best_layout = {'rows': 1, 'cols': panel_count, 'efficiency': 0}
    
    for cols in range(1, panel_count + 1):
        rows = (panel_count + cols - 1) // cols  # Ceiling division
        
        if rows * cols >= panel_count:
            # Calculate how well this layout fits the space
            panel_width = available_width / cols
            panel_height = available_height / rows
            
            # Prefer layouts closer to realistic panel proportions (1.6:1)
            aspect_ratio = panel_width / panel_height if panel_height > 0 else 0
            ideal_aspect = 1.6
            aspect_score = 1 - abs(aspect_ratio - ideal_aspect) / ideal_aspect
            
            # Prefer more compact layouts (less rows usually better)
            compactness_score = 1 / rows
            
            # Overall efficiency
            efficiency = aspect_score * 0.7 + compactness_score * 0.3
            
            if efficiency > best_layout['efficiency']:
                best_layout = {'rows': rows, 'cols': cols, 'efficiency': efficiency}
    
    return best_layout

def validate_image_format(image_data: str) -> bool:
    """Validate if the image data is in correct base64 format"""
    try:
        if not image_data.startswith('data:image/'):
            return False
        
        # Extract base64 data
        base64_data = image_data.split(',')[1] if ',' in image_data else image_data
        
        # Try to decode
        decoded_data = base64.b64decode(base64_data)
        
        # Try to open as PIL image
        img = PILImage.open(BytesIO(decoded_data))
        img.verify()
        
        return True
    except Exception:
        return False

def convert_uploaded_file_to_base64(file_content: bytes, content_type: str) -> str:
    """Convert uploaded file content to base64 data URL"""
    try:
        base64_data = base64.b64encode(file_content).decode('utf-8')
        return f"data:{content_type};base64,{base64_data}"
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error converting image: {str(e)}")

# =============================================================================
# END ROOF VISUALIZATION FUNCTIONS
# =============================================================================

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
async def calculate_solar_solution(client_id: str, region: str = "france", calculation_mode: str = "realistic", manual_kit_power: Optional[int] = None, discount_amount: Optional[int] = None, battery_selected: Optional[bool] = None):
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
                kit_info = SOLAR_KITS[manual_kit_power]  # Use integer key, not string
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
        
        # Calculer le coût batterie si sélectionnée
        battery_cost = 5000 if battery_selected else 0
        
        # Calculate financing options with region-specific rates
        kit_price = kit_info['price_ttc'] if region == "martinique" else kit_info['price']
        financing_options = calculate_financing_options(kit_price, monthly_savings, region, discount_amount or 0, battery_cost)
        
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
        financing_with_aids = calculate_financing_with_aids(kit_price, total_aids, monthly_savings, region, financing_options, discount_amount or 0, battery_cost)
        
        # Calculate all financing options with aids deducted for all durations
        all_financing_with_aids = calculate_all_financing_with_aids(kit_price, total_aids, monthly_savings, region, discount_amount or 0, battery_cost)
        
        # Calculer le nombre de panneaux selon la région
        if region == "martinique":
            # Pour Martinique, calculer les panneaux basé sur la puissance (1 panneau = 375W)
            panel_count = round(kit_info['power'] * 1000 / 375)  # 1kW = 2.67 panneaux de 375W
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
            "annual_edf_bill": annual_edf_bill,
            "discount_applied": discount_amount or 0,  # ✅ AJOUT: Retourner la remise appliquée
            "kit_price_original": kit_price,  # ✅ AJOUT: Prix original avant remise
            "kit_price_final": kit_price - (discount_amount or 0) + battery_cost,  # ✅ AJOUT: Prix final après remise + batterie
            "battery_selected": battery_selected or False,  # ✅ AJOUT: Statut de la batterie
            "battery_cost": battery_cost  # ✅ AJOUT: Coût de la batterie
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
            ['Panneaux photovoltaïques:', f'{calculation_data["panel_count"]} × 375W monocristallin' if calculation_data.get("region") == 'martinique' else f'{calculation_data["panel_count"]} × 500W monocristallin'],
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

def generate_france_renov_martinique_pdf(client_data: dict, calculation_data: dict, client_consumption: float) -> bytes:
    """Generate PDF EXACTLY matching SYRIUS original format - image full page without borders"""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        import requests
        from PIL import Image as PILImage
        import io
        
        # Create PDF buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                              rightMargin=0, leftMargin=0, 
                              topMargin=0, bottomMargin=0)
        
        # Story (content) list
        story = []
        
        # 1. BACKGROUND IMAGE - JUSQU'EN HAUT DE LA PAGE (comme SYRIUS original)
        try:
            toiture_url = "https://customer-assets.emergentagent.com/job_quote-sun-power/artifacts/vtnmxdi2_Toiture%20martinique.bmp"
            response = requests.get(toiture_url, timeout=10)
            if response.status_code == 200:
                img_data = io.BytesIO(response.content)
                pil_img = PILImage.open(img_data)
                img_buffer = io.BytesIO()
                pil_img.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                
                # IMAGE JUSQU'EN HAUT - couvre la moitié supérieure de la page
                bg_img = Image(img_buffer, width=21*cm, height=15*cm)
                story.append(bg_img)
                
                # Retour en arrière pour superposer les éléments
                story.append(Spacer(1, -15*cm))
                
        except Exception as e:
            logging.warning(f"Could not load background image: {e}")
            story.append(Spacer(1, 2*cm))
        
        # Espacement minimal pour positionner le logo
        story.append(Spacer(1, 0.5*cm))
        
        # 2. LOGOS FRH - UN À GAUCHE ET UN À DROITE (même hauteur et dimensions)
        try:
            logo_url = "https://customer-assets.emergentagent.com/job_eco-quote-generator/artifacts/e1vs6tn9_LOGO%20FRH.jpg"
            response = requests.get(logo_url, timeout=10)
            if response.status_code == 200:
                logo_data = io.BytesIO(response.content)
                # LOGO GAUCHE
                logo_left = Image(logo_data, width=5*cm, height=2.5*cm)
                
                # Réinitialiser le buffer pour le deuxième logo
                logo_data.seek(0)
                # LOGO DROITE (même taille exacte)
                logo_right = Image(logo_data, width=5*cm, height=2.5*cm)
                
                # Position des deux logos à la même hauteur
                logo_table = Table([[logo_left, '', logo_right]], colWidths=[5*cm, 11*cm, 5*cm])
                logo_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (0, 0), 'LEFT'),   # Logo gauche
                    ('ALIGN', (2, 0), (2, 0), 'RIGHT'),  # Logo droite
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (0, 0), 1*cm),
                    ('RIGHTPADDING', (2, 0), (2, 0), 1*cm),
                ]))
                story.append(logo_table)
        except Exception as e:
            logging.warning(f"Could not load FRH logo: {e}")
        
        # Espacement vers le centre
        story.append(Spacer(1, 5*cm))
        
        # 3. CARRÉS BLANC ET ORANGE - EXACTEMENT MÊME TAILLE ET PARFAITEMENT CENTRÉS
        client_name = f"{client_data.get('first_name', '')} {client_data.get('last_name', '')}"
        client_address = client_data.get('address', '')
        
        # CARRÉ BLANC - "VOTRE ÉTUDE PERSONNALISÉE" (taille exacte)
        white_box_content = [
            [Paragraph('<b>VOTRE ÉTUDE<br/>PERSONNALISÉE</b>', ParagraphStyle(
                'SYRIUSTitle',
                parent=getSampleStyleSheet()['Normal'],
                fontSize=18,
                textColor=colors.black,
                alignment=0,  # Left align comme SYRIUS
                fontName='Helvetica-Bold',
                spaceAfter=10,
                leading=22
            ))],
            [Paragraph('Merci de nous solliciter pour<br/>votre projet d\'installation solaire<br/>en autoconsommation', ParagraphStyle(
                'SYRIUSSubtitle',
                parent=getSampleStyleSheet()['Normal'],
                fontSize=11,
                textColor=colors.HexColor('#666666'),
                alignment=0,  # Left align comme SYRIUS
                fontName='Helvetica',
                leading=14
            ))]
        ]
        
        # CARRÉ ORANGE - COORDONNÉES CLIENT (même taille exacte avec police encore plus grande)
        client_box_content = [
            [Paragraph(f'<b>Nom : {client_name}</b><br/><b>Adresse : {client_address}</b>', ParagraphStyle(
                'SYRIUSClientInfo',
                parent=getSampleStyleSheet()['Normal'],
                fontSize=14,  # ENCORE AGRANDIE de 13pt à 14pt
                textColor=colors.white,
                fontName='Helvetica-Bold',
                alignment=0,  # Left align
                leading=17    # Ajusté pour la nouvelle taille 14pt
            ))]
        ]
        
        # CARRÉ BLANC (taille identique)
        white_box_table = Table(white_box_content, colWidths=[8*cm], rowHeights=[1.5*cm, 2.5*cm])
        white_box_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 20),
            ('RIGHTPADDING', (0, 0), (-1, -1), 20),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
        ]))
        
        # CARRÉ ORANGE (taille EXACTEMENT identique)
        client_box_table = Table(client_box_content, colWidths=[8*cm], rowHeights=[4*cm])
        client_box_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FF9800')),  # Orange comme SYRIUS
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ]))
        
        # PARFAITEMENT CENTRÉS avec espace entre les carrés
        combined_boxes = Table([
            ['', white_box_table, '', client_box_table, '']
        ], colWidths=[2.5*cm, 8*cm, 0.5*cm, 8*cm, 2.5*cm])
        combined_boxes.setStyle(TableStyle([
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),   # Carré blanc centré
            ('ALIGN', (3, 0), (3, 0), 'CENTER'),   # Carré orange centré
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(combined_boxes)
        
        # Espacement AUGMENTÉ pour redescendre le texte
        story.append(Spacer(1, 4*cm))
        
        # TEXTE PRINCIPAL avec justification ET police à 13pt (version précédente)
        main_text_style = ParagraphStyle(
            'SYRIUSMainText',
            parent=getSampleStyleSheet()['Normal'],
            fontSize=13,  # Retour à 13pt (juste avant la dernière modification)
            textColor=colors.black,
            fontName='Helvetica',
            alignment=4,  # JUSTIFY pour étaler le texte
            spaceAfter=6,
            leading=16    # Retour à 16pt pour la taille 13
        )
        
        # Container avec largeur optimale pour justification
        text_container = Table([
            [Paragraph('<b>Madame / Monsieur</b>', main_text_style)],
            [Paragraph('Conformément à notre échange, nous avons le plaisir de vous adresser votre', main_text_style)],
            [Paragraph("rapport d'étude personnalisée pour votre projet d'autoconsommation solaire.", main_text_style)],
            [Paragraph("Vous trouverez ci-après les détails de votre installation.", main_text_style)],
            [Paragraph("", main_text_style)],  # LIGNE VIDE ajoutée
            [Paragraph("Nous restons à votre entière disposition, si besoin, pour tout complément", main_text_style)],
            [Paragraph("d'information.", main_text_style)],
            [Paragraph('<b>Bonne journée</b>', main_text_style)]
        ], colWidths=[18*cm])
        
        text_container.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 1*cm),
            ('RIGHTPADDING', (0, 0), (-1, -1), 1*cm),
        ]))
        
        story.append(text_container)
        
        # ESPACEMENT RÉDUIT pour que le footer reste sur page 1
        story.append(Spacer(1, 4*cm))
        
        # Espacement final pour footer (RESTE SUR PAGE 1)
        story.append(Spacer(1, 1*cm))
        
        # FOOTER - COORDONNÉES FRH EN BAS DE PAGE 1 (comme SYRIUS)
        footer_style = ParagraphStyle(
            'SYRIUSFooter',
            parent=getSampleStyleSheet()['Normal'],
            fontSize=9,
            textColor=colors.black,
            fontName='Helvetica',
            alignment=1,  # Center
            leading=11
        )
        
        # Footer sur 2 lignes EN BAS DE LA PAGE 1
        footer_line1 = "<b>F.R.H Environnement SAS</b> - 11 rue des Arts et Métiers, Fort-de-France - Tél. 09 85 60 50 51 - direction@francerenovhabitat.com"
        footer_line2 = "Capital social de 30 000 € - Siret : 890 493 737 00013 - N° TVA Intra : FR52890493737 - Site Web: france-renovhabitat.fr - N° convention: N2024KPV516"
        
        story.append(Paragraph(footer_line1, footer_style))
        story.append(Spacer(1, 0.1*cm))
        story.append(Paragraph(footer_line2, footer_style))
        
        # Import PageBreak for second page
        from reportlab.platypus import PageBreak
        
        # PAGE 2 - VOTRE PROJET SOLAIRE EN DÉTAIL (COPIE EXACTE SYRIUS)
        story.append(PageBreak())
        
        # 1. IMAGE DE TOIT FRH MARTINIQUE EN HAUT
        try:
            # Utiliser la vraie photo FRH Martinique uploadée par l'utilisateur
            frh_image_url = "https://customer-assets.emergentagent.com/job_eco-quote-solar/artifacts/lvrbkle1_WhatsApp%20Image%202025-08-01%20%C3%A0%2010.32.11_f5adca3a.jpg"
            response = requests.get(frh_image_url, timeout=10)
            if response.status_code == 200:
                img_data = io.BytesIO(response.content)
                pil_img = PILImage.open(img_data)
                img_buffer = io.BytesIO()
                pil_img.save(img_buffer, format='JPEG')
                img_buffer.seek(0)
                
                # Image comme dans SYRIUS original - taille et position exactes
                roof_img = Image(img_buffer, width=21*cm, height=8*cm)
                story.append(roof_img)
                story.append(Spacer(1, 1*cm))
                
        except Exception as e:
            logging.warning(f"Could not load FRH Martinique image: {e}")
            story.append(Spacer(1, 3*cm))
        
        # 2. TITRE PRINCIPAL EXACTEMENT COMME SYRIUS
        title_style_page2 = ParagraphStyle(
            'SYRIUSTitlePage2',
            parent=getSampleStyleSheet()['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#FF9800'),  # Orange comme SYRIUS
            fontName='Helvetica-Bold',
            alignment=1,  # Center
            spaceAfter=20,
            spaceBefore=10
        )
        
        story.append(Paragraph("VOTRE PROJET SOLAIRE EN DÉTAIL !", title_style_page2))
        story.append(Spacer(1, 0.5*cm))
        
        # 3. TEXTE DESCRIPTIF IDENTIQUE À SYRIUS - PLUS GROS POUR 6 LIGNES
        descriptive_style = ParagraphStyle(
            'SYRIUSDescriptive',
            parent=getSampleStyleSheet()['Normal'],
            fontSize=13,  # Augmenté de 11 à 13 pour faire 6 lignes
            textColor=colors.black,
            fontName='Helvetica',
            alignment=4,  # Justify comme SYRIUS
            spaceAfter=8,
            leading=16,   # Augmenté pour plus d'espace entre lignes
            leftIndent=1*cm,
            rightIndent=1*cm
        )
        
        descriptive_text = """L'objectif est de vous faire réaliser le maximum d'économies en installant une centrale solaire dimensionnée de manière optimale par rapport à votre logement et vos habitudes de vie.

Grâce à ce projet, vous allez pouvoir capitaliser en devenant propriétaire de votre générateur solaire avec une production énergétique garantie pendant 25 ans minimum."""
        
        story.append(Paragraph(descriptive_text, descriptive_style))
        story.append(Spacer(1, 1*cm))
        
        # 4. PUISSANCE SOLAIRE PROPOSÉE DANS RECTANGLE VERT (EXACTEMENT COMME SYRIUS)
        if calculation_data:
            kit_power = calculation_data.get('recommended_kit_power', 6) * 1000  # Convertir en Wc
            autonomy = calculation_data.get('autonomy_percentage', 67)
            
            # RECTANGLE VERT EXACTEMENT COMME L'ORIGINAL SYRIUS (mais vert au lieu d'orange)
            power_box_data = [
                [Paragraph(f"Puissance solaire proposée<br/>{kit_power:,} Wc", ParagraphStyle(
                    'PowerBoxText',
                    parent=getSampleStyleSheet()['Normal'],
                    fontSize=16,
                    textColor=colors.white,
                    fontName='Helvetica-Bold',
                    alignment=1,  # Center
                    leading=20,
                    spaceAfter=0,
                    spaceBefore=0
                ))]
            ]
            
            # Créer le tableau pour le rectangle vert - même taille que SYRIUS
            power_box_table = Table(power_box_data, colWidths=[8*cm], rowHeights=[3*cm])
            power_box_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#4CAF50')),  # VERT au lieu d'orange
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0, colors.white),  # Pas de bordure visible
            ]))
            
            # Centrer le rectangle comme dans SYRIUS
            power_container = Table([['', power_box_table, '']], colWidths=[6.5*cm, 8*cm, 6.5*cm])
            power_container.setStyle(TableStyle([
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            story.append(power_container)
            story.append(Spacer(1, 0.8*cm))
            
            # Taux d'autoconsommation EXACTEMENT comme SYRIUS (EN GRAS sur 2 lignes)
            auto_style = ParagraphStyle(
                'SYRIUSAuto',
                parent=getSampleStyleSheet()['Normal'],
                fontSize=12,
                textColor=colors.black,
                fontName='Helvetica-Bold',  # EN GRAS comme l'original
                alignment=1,  # Center
                spaceAfter=15,
                leading=16,   # Plus d'espace pour 2 lignes
                leftIndent=1*cm,
                rightIndent=1*cm
            )
            
            # Texte sur 2 lignes comme l'original
            auto_text = f"Taux d'auto-consommation estimé selon<br/>les hypothèses de l'étude : {autonomy} %"
            story.append(Paragraph(auto_text, auto_style))
            story.append(Spacer(1, 0.5*cm))
            
            # 5. DONNÉES PRINCIPALES - STYLE EXACTEMENT COMME SYRIUS
            data_title_style = ParagraphStyle(
                'SYRIUSDataTitle',
                parent=getSampleStyleSheet()['Normal'],
                fontSize=11,
                textColor=colors.black,
                fontName='Helvetica-Bold',
                alignment=0,  # Left
                spaceAfter=10,
                leftIndent=1*cm
            )
            
            story.append(Paragraph("Principales données pour le calcul de votre centrale solaire :", data_title_style))
            
            # CORRECTION : Utiliser la vraie consommation client passée en paramètre
            annual_consumption = client_consumption  # Vraie consommation client (ex: 5890)
            
            # Récupérer les calculs de production - UTILISER LES MÊMES DONNÉES QUE L'INTERFACE
            # DEBUG: Afficher toutes les clés disponibles pour identifier le problème
            import logging
            logging.warning(f"DEBUG PDF - Clés disponibles dans calculation_data: {list(calculation_data.keys())}")
            logging.warning(f"DEBUG PDF - estimated_production: {calculation_data.get('estimated_production')}")
            logging.warning(f"DEBUG PDF - annual_production: {calculation_data.get('annual_production')}")
            logging.warning(f"DEBUG PDF - kit_power: {calculation_data.get('kit_power')}")
            
            annual_production = calculation_data.get('estimated_production', 8902)  # Même champ que l'interface
            autoconsumption_kwh = calculation_data.get('autoconsumption_kwh', 7567)
            surplus_kwh = calculation_data.get('surplus_kwh', 1335)
            
            # DEBUG: Vérifier les valeurs récupérées
            logging.warning(f"DEBUG PDF - annual_production utilisée: {annual_production}")
            logging.warning(f"DEBUG PDF - autoconsumption_kwh: {autoconsumption_kwh}")
            logging.warning(f"DEBUG PDF - surplus_kwh: {surplus_kwh}")
            
            data_style = ParagraphStyle(
                'SYRIUSData',
                parent=getSampleStyleSheet()['Normal'],
                fontSize=11,
                textColor=colors.black,
                fontName='Helvetica',
                alignment=0,  # Left
                spaceAfter=5,
                leftIndent=1*cm,
                rightIndent=1*cm,
                leading=16
            )
            
            # Données formatées avec CHIFFRES EN COULEUR ET EN GRAS - FORMAT FRANÇAIS CORRECT
            data_text = f"""
Consommation annuelle actuelle : <font color="red"><b>{annual_consumption:,.0f} kWh</b></font><br/>
Production solaire annuelle estimée : <font color="green"><b>{annual_production:,.0f} kWh</b></font><br/>
Dont <font color="green"><b>{autoconsumption_kwh:,.0f} kWh</b></font> sont autoconsommés<br/>
Dont <font color="green"><b>{surplus_kwh:,.0f} kWh</b></font> sont réinjectés dans le réseau
"""
            
            # Remplacer les points par des virgules (format français) - APRÈS formatage
            data_text = data_text.replace(',', ' ')  # Remplacer seulement les séparateurs de milliers
            
            story.append(Paragraph(data_text, data_style))
            story.append(Spacer(1, 1*cm))
        
        # 6. PHRASE FINALE IDENTIQUE SYRIUS
        footer_text_style = ParagraphStyle(
            'SYRIUSFooterText',
            parent=getSampleStyleSheet()['Normal'],
            fontSize=9,
            textColor=colors.black,
            fontName='Helvetica',
            alignment=4,  # Justify
            spaceAfter=8,
            leading=11,
            leftIndent=1*cm,
            rightIndent=1*cm
        )
        
        pvgis_text = """Cette estimation indicative et non contractuelle a été effectuée à l'aide du logiciel européen PVGIS. Elle repose sur l'orientation et l'inclinaison de la toiture, ainsi que sur les informations fournies par le client, en tenant compte des scénarios statistiques. L'économie estimée prend en considération les modifications de comportement du client."""
        
        story.append(Paragraph(pvgis_text, footer_text_style))
        story.append(Spacer(1, 1*cm))  # Réduit de 2cm à 1cm
        
        # 7. FOOTER FRH MARTINIQUE (remplace Syrius) - RESTE EN BAS DE PAGE 2
        frh_footer_style = ParagraphStyle(
            'FRHFooter',
            parent=getSampleStyleSheet()['Normal'],
            fontSize=9,
            textColor=colors.black,
            fontName='Helvetica',
            alignment=1,  # Center
            leading=11
        )
        
        # Coordonnées FRH Martinique
        frh_footer_text = """<b>F.R.H Environnement SAS</b> - 11 rue des Arts et Métiers, Fort-de-France - Tél. 09 85 60 50 51 - direction@francerenovhabitat.com<br/>
Capital social de 30 000 € - Siret : 890 493 737 00013 - N° TVA Intra : FR52890493737 - Site Web: france-renovhabitat.fr - N° convention: N2024KPV516"""
        
        story.append(Paragraph(frh_footer_text, frh_footer_style))
        
        # Build PDF
        doc.build(story)
        
        # Get the PDF bytes
        buffer.seek(0)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
        
    except Exception as e:
        logging.error(f"Error generating SYRIUS exact copy PDF: {e}")
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

@api_router.get("/generate-france-renov-martinique-pdf/{client_id}")
async def generate_france_renov_martinique_devis(client_id: str):
    """Generate France Renov Martinique PDF for client (SYRIUS format)"""
    try:
        # Get client data
        client = await db.clients.find_one({"id": client_id})
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Calculate solar data
        calculation_response = await calculate_solar_solution(
            client_id=client_id,
            battery_selected=False,
            discount_amount=0,
            manual_kit_power=None,
            region="martinique"  # Force Martinique region
        )
        
        # CORRECTION : Récupérer la consommation DIRECTEMENT depuis les données client
        # car elle n'est pas incluse dans la réponse calculate
        client_consumption = client.get('annual_consumption_kwh', 0)
        
        # Generate France Renov Martinique PDF avec la vraie consommation client
        pdf_bytes = generate_france_renov_martinique_pdf(client, calculation_response, client_consumption)
        
        # Create filename
        client_name = f"{client['first_name']}_{client['last_name']}"
        filename = f"etude_solaire_{client_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        # Return PDF
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logging.error(f"Error generating France Renov Martinique PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
- Puissance d'un panneau 375W
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
                "panels": kit_data["panels"],  # Ajouter le nombre de panneaux
                "price_ht": kit_data["price_ttc"],  # Prix TTC pour Martinique
                "price_ttc": kit_data["price_ttc"],
                "aid_amount": kit_data["aid_amount"],
                "surface": kit_data["surface"],
                "co2_savings": kit_data["price_ttc"] * 0.15  # 15% comme commission CO2
            })
        return {"kits": kits}
    else:
        # Pour la France, utiliser les kits fixes depuis SOLAR_KITS
        kits = []
        for power, kit_data in SOLAR_KITS.items():
            kits.append({
                "id": f"kit_{power}kw",
                "name": f"Kit {power}kW",
                "power": power,
                "panels": kit_data["panels"],
                "price_ht": kit_data["price"],  # Prix HT 
                "price_ttc": kit_data["price"],  # Prix TTC identique pour France
                "aid_amount": 0,  # À calculer dynamiquement
                "surface": kit_data["panels"] * 2.1,  # Surface en m²
                "co2_savings": 2500  # CO2 économisé par an en kilos
            })
        return {"kits": kits}

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

# =============================================================================
# PDF FRH MARTINIQUE GENERATION ENDPOINT - MOVE BEFORE ROUTER INCLUSION
# =============================================================================

# Informations FRH Martinique Environnement
FRH_MARTINIQUE_INFO = {
    "company_name": "FRH Martinique Environnement",
    "address": "Centre d'affaires à Fort-de-France, Martinique", 
    "phone": "+33 6 52 43 62 47",
    "email": "frhmartinique@francerenovhabitat.com",
    "website": "https://frh-martinique.fr/",
    "tva_intra": "FR52890493737",
    "convention_number": "N2024KPV516",
    "siret": "890 493 737 00013",
    "rcs": "890493737",
    "naf": "4322B",
    "commercial_contact": "Martis Philippe",
    "commercial_phone": "06 22 70 07 45",
    "commercial_email": "philippefrhpro@gmail.com",
    "warranty": "Toutes nos installations bénéficient d'une garantie de 10 ans"
}

def create_simple_professional_frh_pdf(client_data: dict, calculation_results: dict) -> bytes:
    """
    Crée un PDF simple mais professionnel FRH Martinique avec toutes les données
    """
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                              rightMargin=50, leftMargin=50,
                              topMargin=50, bottomMargin=50)
        
        # Styles professionnels
        styles = getSampleStyleSheet()
        
        # Styles personnalisés FRH
        title_style = ParagraphStyle(
            'FRHTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=20,
            textColor=colors.darkgreen,
            fontName='Helvetica-Bold',
            alignment=1  # Centré
        )
        
        heading_style = ParagraphStyle(
            'FRHHeading',
            parent=styles['Heading2'],
            fontSize=18,
            spaceAfter=15,
            textColor=colors.darkgreen,
            fontName='Helvetica-Bold'
        )
        
        normal_style = ParagraphStyle(
            'FRHNormal',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=10,
            fontName='Helvetica'
        )
        
        bold_style = ParagraphStyle(
            'FRHBold',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=10,
            fontName='Helvetica-Bold'
        )
        
        content = []
        
        # ================================================================
        # PAGE 1 - EN-TÊTE AVEC LOGO FRH ET DONNÉES CLIENT
        # ================================================================
        
        # Logo FRH (nouveau logo fourni)
        logo_path = "/app/backend/frh_logo_new.bmp"
        try:
            logo_img = Image(logo_path, width=200, height=100)
            logo_table = Table([[logo_img]], colWidths=[200])
            logo_table.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
            content.append(logo_table)
            content.append(Spacer(1, 20))
        except Exception as e:
            logging.error(f"Erreur chargement logo: {e}")
            content.append(Paragraph("FRH MARTINIQUE ENVIRONNEMENT", title_style))
            content.append(Spacer(1, 20))
        
        # Titre principal
        content.append(Paragraph("ÉTUDE PERSONNALISÉE", title_style))
        content.append(Paragraph("INSTALLATION PHOTOVOLTAÏQUE", title_style))
        content.append(Spacer(1, 30))
        
        # Zone client (simple mais propre)
        client_name = f"{client_data.get('first_name', '')} {client_data.get('last_name', '')}"
        
        client_info = [
            ["👤 CLIENT", ""],
            ["Nom complet", client_name],
            ["Adresse", client_data.get('address', '')],
            ["Téléphone", client_data.get('phone', '')],
            ["Email", client_data.get('email', '')],
            ["Date de l'étude", datetime.now().strftime('%d/%m/%Y')]
        ]
        
        client_table = Table(client_info, colWidths=[3*inch, 3.5*inch])
        client_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.Color(0.95, 0.98, 0.95)),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 11)
        ]))
        content.append(client_table)
        content.append(Spacer(1, 30))
        
        # Coordonnées FRH
        frh_info = [
            ["🏢 FRH MARTINIQUE ENVIRONNEMENT", ""],
            ["Adresse", FRH_MARTINIQUE_INFO['address']],
            ["Téléphone", FRH_MARTINIQUE_INFO['phone']],
            ["Email", FRH_MARTINIQUE_INFO['email']],
            ["Site web", FRH_MARTINIQUE_INFO['website']],
            ["Contact commercial", f"{FRH_MARTINIQUE_INFO['commercial_contact']} - {FRH_MARTINIQUE_INFO['commercial_phone']}"]
        ]
        
        frh_table = Table(frh_info, colWidths=[3*inch, 3.5*inch])
        frh_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.2, 0.4, 0.8)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.Color(0.9, 0.95, 1)),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 11)
        ]))
        content.append(frh_table)
        
        content.append(PageBreak())
        
        # ================================================================
        # PAGE 2 - VOTRE PROJET SOLAIRE
        # ================================================================
        
        content.append(Paragraph("VOTRE PROJET SOLAIRE", title_style))
        content.append(Spacer(1, 20))
        
        content.append(Paragraph("Nous avons étudié votre projet d'installation photovoltaïque en tenant compte de vos besoins énergétiques et des spécificités de votre logement en Martinique.", normal_style))
        content.append(Spacer(1, 20))
        
        # Données du projet
        if calculation_results:
            kit_power = calculation_results.get('recommended_kit_power', 6)
            panels_count = calculation_results.get('panels', 16)
            annual_production = calculation_results.get('annual_production', 8902)
            autonomy = calculation_results.get('autonomy_percentage', 100)
            
            project_info = [
                ["📊 CONFIGURATION RECOMMANDÉE", ""],
                ["Puissance installée", f"{kit_power} kWc"],
                ["Nombre de panneaux", f"{panels_count} Panneaux POWERNITY 375W"],
                ["Micro-onduleurs", "TECH 360"],
                ["Production annuelle estimée", f"{annual_production:.0f} kWh/an"],
                ["Taux d'autoconsommation", f"{autonomy}%"],
                ["Économies annuelles estimées", f"{calculation_results.get('estimated_savings', 2166):.0f} €/an"]
            ]
            
            project_table = Table(project_info, colWidths=[4*inch, 2.5*inch])
            project_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.95, 0.6, 0.1)),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.Color(1, 0.98, 0.9)),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold')
            ]))
            content.append(project_table)
            content.append(Spacer(1, 30))
        
        # Avantages
        content.append(Paragraph("✅ AVANTAGES DE VOTRE INSTALLATION", heading_style))
        avantages = [
            "• Installation certifiée RGE par nos équipes locales",
            "• Garantie panneaux 25 ans + micro-onduleurs 12 ans",
            "• Maintenance et SAV local en Martinique",
            "• Réduction drastique de vos factures EDF",
            "• Valorisation de votre bien immobilier",
            "• Geste écologique pour l'environnement"
        ]
        
        for avantage in avantages:
            content.append(Paragraph(avantage, normal_style))
        
        content.append(PageBreak())
        
        # ================================================================
        # PAGE 3 - ANALYSE FINANCIÈRE DÉTAILLÉE
        # ================================================================
        
        content.append(Paragraph("ANALYSE FINANCIÈRE", title_style))
        content.append(Spacer(1, 20))
        
        if calculation_results:
            # Calcul des prix selon le kit
            price_estimates = {
                3: {"ttc": 10900, "aide": 5340},
                6: {"ttc": 15900, "aide": 6480},
                9: {"ttc": 18900, "aide": 9720},
                12: {"ttc": 22900, "aide": 9720},
                15: {"ttc": 25900, "aide": 12150},
                18: {"ttc": 28900, "aide": 14580},
                21: {"ttc": 30900, "aide": 17010},
                24: {"ttc": 32900, "aide": 19440},
                27: {"ttc": 34900, "aide": 21870}
            }
            
            closest_power = min(price_estimates.keys(), key=lambda x: abs(x - kit_power))
            price_info = price_estimates[closest_power]
            
            # Vérifier les remises R1/R2/R3
            discount_amount = calculation_results.get('discount_applied', 0)
            final_ttc = price_info['ttc'] - discount_amount
            final_with_aids = final_ttc - price_info['aide']
            
            # Tableau des prix
            price_data = [
                ["💰 INVESTISSEMENT", "MONTANT"],
                ["Prix TTC hors primes", f"{final_ttc:,} €".replace(',', ' ')],
                ["Primes d'investissement", f"- {price_info['aide']:,} €".replace(',', ' ')],
                ["PRIX FINAL TTC", f"{final_with_aids:,} €".replace(',', ' ')]
            ]
            
            # Ajouter la remise si applicable
            if discount_amount > 0:
                price_data.insert(2, ["Remise exceptionnelle", f"- {discount_amount:,} €".replace(',', ' ')])
            
            price_table = Table(price_data, colWidths=[4*inch, 2.5*inch])
            price_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('BACKGROUND', (0, -1), (-1, -1), colors.Color(0.95, 0.6, 0.1)),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('FONTSIZE', (0, -1), (-1, -1), 16),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, -1), (-1, -1), 12),
                ('BACKGROUND', (0, 1), (-1, -2), colors.Color(0.98, 0.98, 0.98)),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -2), 12)
            ]))
            content.append(price_table)
            content.append(Spacer(1, 30))
        
        # Analyse économique
        content.append(Paragraph("📈 VOS ÉCONOMIES D'ÉNERGIE", heading_style))
        
        if calculation_results:
            monthly_savings = calculation_results.get('estimated_savings', 2166) / 12
            annual_edf = client_data.get('annual_edf_payment', 2640)
            
            savings_data = [
                ["COMPARAISON", "SANS PV", "AVEC PV", "ÉCONOMIES"],
                ["Facture mensuelle", f"{client_data.get('monthly_edf_payment', 220)} €", f"{client_data.get('monthly_edf_payment', 220) - monthly_savings:.0f} €", f"{monthly_savings:.0f} €"],
                ["Facture annuelle", f"{annual_edf} €", f"{annual_edf - calculation_results.get('estimated_savings', 2166):.0f} €", f"{calculation_results.get('estimated_savings', 2166):.0f} €"],
                ["Sur 20 ans", f"{annual_edf * 20:,} €".replace(',', ' '), f"{(annual_edf - calculation_results.get('estimated_savings', 2166)) * 20:,} €".replace(',', ' '), f"{calculation_results.get('estimated_savings', 2166) * 20:,} €".replace(',', ' ')]
            ]
            
            savings_table = Table(savings_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
            savings_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.2, 0.4, 0.8)),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('BACKGROUND', (3, 1), (3, -1), colors.Color(0.9, 1, 0.9)),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 10)
            ]))
            content.append(savings_table)
            content.append(Spacer(1, 20))
            
            # Rentabilité
            if 'price_info' in locals():
                payback_years = (final_ttc - price_info['aide']) / calculation_results.get('estimated_savings', 2166)
                content.append(Paragraph(f"💡 <b>Durée d'amortissement estimée : {payback_years:.1f} ans</b>", bold_style))
        
        content.append(PageBreak())
        
        # ================================================================
        # PAGE 4 - DEVIS FINAL
        # ================================================================
        
        content.append(Paragraph("DEVIS FINAL", title_style))
        content.append(Spacer(1, 20))
        
        # Numéro de devis unique
        devis_number = f"FRH-{datetime.now().strftime('%Y%m%d')}-{client_data.get('id', 'XXXX')[:4]}"
        content.append(Paragraph(f"<b>N° de devis :</b> {devis_number}", bold_style))
        content.append(Paragraph(f"<b>Date :</b> {datetime.now().strftime('%d/%m/%Y')}", bold_style))
        content.append(Spacer(1, 20))
        
        # Récapitulatif installation
        if calculation_results:
            recap_data = [
                ["🔧 INSTALLATION PHOTOVOLTAÏQUE", ""],
                ["Pack sélectionné", f"{kit_power} kWc"],
                ["Panneaux", f"{panels_count} x POWERNITY 375W"],
                ["Micro-onduleurs", "TECH 360"],
                ["Installation", "Pose en surimposition"],
                ["Raccordement", "Monophasé"],
                ["Garanties", "Panneaux 25 ans / Onduleurs 12 ans"],
                ["Main d'œuvre", "Garantie 10 ans"]
            ]
            
            recap_table = Table(recap_data, colWidths=[4*inch, 2.5*inch])
            recap_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.95, 0.6, 0.1)),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.Color(1, 0.98, 0.9)),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 11)
            ]))
            content.append(recap_table)
            content.append(Spacer(1, 30))
            
            # Prix final répété
            final_price_data = [
                ["MONTANT TOTAL TTC", f"{final_with_aids:,} €".replace(',', ' ')]
            ]
            
            final_price_table = Table(final_price_data, colWidths=[4*inch, 2.5*inch])
            final_price_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.darkgreen),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 18),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
                ('GRID', (0, 0), (-1, -1), 2, colors.white)
            ]))
            content.append(final_price_table)
        
        content.append(Spacer(1, 40))
        
        # Informations légales FRH
        legal_data = [
            ["📋 INFORMATIONS LÉGALES", ""],
            ["SIRET", FRH_MARTINIQUE_INFO['siret']],
            ["N° TVA Intracommunautaire", FRH_MARTINIQUE_INFO['tva_intra']],
            ["RCS", FRH_MARTINIQUE_INFO['rcs']],
            ["Code NAF", FRH_MARTINIQUE_INFO['naf']],
            ["N° de convention", FRH_MARTINIQUE_INFO['convention_number']],
            ["Assurance", FRH_MARTINIQUE_INFO['warranty']]
        ]
        
        legal_table = Table(legal_data, colWidths=[3*inch, 3.5*inch])
        legal_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.5, 0.5, 0.5)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.Color(0.95, 0.95, 0.95)),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10)
        ]))
        content.append(legal_table)
        
        # Build PDF
        doc.build(content)
        buffer.seek(0)
        return buffer.getvalue()
        
    except Exception as e:
        logging.error(f"Erreur création PDF FRH simple: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur génération PDF: {str(e)}")

# ================================================================
# ROOF VISUALIZATION ENDPOINTS
# ================================================================

@api_router.post("/upload-roof-image", response_model=ImageUploadResponse)
async def upload_roof_image(file: UploadFile = File(...)):
    """
    Upload a roof image for solar panel visualization
    """
    try:
        # Check file type
        if not file.content_type.startswith('image/'):
            return ImageUploadResponse(
                success=False,
                error_message="File must be an image"
            )
        
        # Check file size (limit to 10MB)
        file_content = await file.read()
        if len(file_content) > 10 * 1024 * 1024:  # 10MB limit
            return ImageUploadResponse(
                success=False,
                error_message="Image file too large (max 10MB)"
            )
        
        # Convert to base64
        base64_image = convert_uploaded_file_to_base64(file_content, file.content_type)
        
        # Validate image format
        if not validate_image_format(base64_image):
            return ImageUploadResponse(
                success=False,
                error_message="Invalid image format"
            )
        
        return ImageUploadResponse(
            success=True,
            image_data=base64_image,
            file_size=len(file_content)
        )
        
    except Exception as e:
        logging.error(f"Error uploading roof image: {str(e)}")
        return ImageUploadResponse(
            success=False,
            error_message=f"Upload error: {str(e)}"
        )

@api_router.post("/generate-roof-visualization", response_model=RoofVisualizationResponse)
async def generate_roof_visualization(request: RoofVisualizationRequest):
    """
    Generate photorealistic solar panel visualization on a roof image
    """
    try:
        # Validate image format
        if not validate_image_format(request.image_data):
            return RoofVisualizationResponse(
                success=False,
                error_message="Invalid image format. Please provide base64 encoded image."
            )
        
        # Validate kit power
        if request.region == "martinique":
            valid_powers = [3, 6, 9, 12, 15, 18, 21, 24, 27]
        else:
            valid_powers = list(SOLAR_KITS.keys())
        
        if request.kit_power not in valid_powers:
            return RoofVisualizationResponse(
                success=False,
                error_message=f"Invalid kit power. Valid options for {request.region}: {valid_powers}"
            )
        
        # Generate visualization using fal.ai
        result = await generate_solar_panel_visualization(
            image_data=request.image_data,
            kit_power=request.kit_power,
            region=request.region
        )
        
        if result["success"]:
            # Get kit information
            if request.region == "martinique":
                region_kits = REGIONS_CONFIG["martinique"]["kits"]
                kit_key = f"kit_{request.kit_power}kw"
                kit_info = region_kits.get(kit_key, {})
            else:
                kit_info = SOLAR_KITS.get(request.kit_power, {})
            
            return RoofVisualizationResponse(
                success=True,
                generated_image_url=result["generated_image_url"],
                original_image_data=request.image_data,
                kit_info={
                    "power": request.kit_power,
                    "panels": result["panel_count"],
                    "region": request.region,
                    **kit_info
                }
            )
        else:
            return RoofVisualizationResponse(
                success=False,
                error_message=result["error_message"]
            )
        
    except Exception as e:
        logging.error(f"Error generating roof visualization: {str(e)}")
        return RoofVisualizationResponse(
            success=False,
            error_message=f"Generation error: {str(e)}"
        )

# ================================================================
# END ROOF VISUALIZATION ENDPOINTS
# ================================================================

@api_router.get("/generate-frh-pdf/{client_id}")
async def generate_frh_pdf(client_id: str):
    """
    Génère un PDF FRH Martinique simple mais professionnel
    """
    try:
        # Récupérer les données client
        client_data = await db.clients.find_one({"id": client_id})
        if not client_data:
            raise HTTPException(status_code=404, detail="Client non trouvé")
        
        # Récupérer les résultats de calcul
        calculation_results = client_data.get('calculation_results', {})
        
        # Générer le PDF simple et professionnel
        pdf_content = create_simple_professional_frh_pdf(client_data, calculation_results)
        
        # Nom du fichier avec date
        filename = f"devis_frh_martinique_{client_data.get('last_name', 'client')}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logging.error(f"Erreur endpoint PDF FRH: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur génération PDF: {str(e)}")

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