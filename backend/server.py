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
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

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
    
    # Client mode
    client_mode: str = "particuliers"  # Nouveau champ pour le mode client
    
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
    roof_surface: float
    roof_orientation: str
    velux_count: int
    heating_system: str
    water_heating_system: str
    water_heating_capacity: Optional[int] = None
    annual_consumption_kwh: float
    monthly_edf_payment: float
    annual_edf_payment: float
    client_mode: str = "particuliers"  # Nouveau champ pour le mode client

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

# Solar Kit Pricing - Particuliers
SOLAR_KITS_PARTICULIERS = {
    3: {"price": 14900, "panels": 6},
    4: {"price": 20900, "panels": 8},
    5: {"price": 21900, "panels": 10},
    6: {"price": 22900, "panels": 12},
    7: {"price": 24900, "panels": 14},
    8: {"price": 26900, "panels": 16},
    9: {"price": 29900, "panels": 18}
}

# Solar Kit Pricing - Professionnels (tarifs HT du tableau PRO)
SOLAR_KITS_PROFESSIONNELS = {
    10: {
        "panels": 24, "surface": 45,
        "prime": 1900, "tarif_rachat_surplus": 0.0761,
        "tarif_base_ht": 18400, "tarif_remise_ht": 17900, "tarif_remise_max_ht": 17400,
        "commission_normale": 1840, "commission_remise_max": 1590
    },
    11: {
        "panels": 26, "surface": 50,
        "prime": 2090, "tarif_rachat_surplus": 0.0761,
        "tarif_base_ht": 20200, "tarif_remise_ht": 19650, "tarif_remise_max_ht": 19100,
        "commission_normale": 2020, "commission_remise_max": 1745
    },
    12: {
        "panels": 29, "surface": 54,
        "prime": 2280, "tarif_rachat_surplus": 0.0761,
        "tarif_base_ht": 22000, "tarif_remise_ht": 21400, "tarif_remise_max_ht": 20800,
        "commission_normale": 2200, "commission_remise_max": 1900
    },
    13: {
        "panels": 31, "surface": 59,
        "prime": 2470, "tarif_rachat_surplus": 0.0761,
        "tarif_base_ht": 23700, "tarif_remise_ht": 23050, "tarif_remise_max_ht": 22400,
        "commission_normale": 2370, "commission_remise_max": 2045
    },
    14: {
        "panels": 33, "surface": 63,
        "prime": 2660, "tarif_rachat_surplus": 0.0761,
        "tarif_base_ht": 25400, "tarif_remise_ht": 24700, "tarif_remise_max_ht": 24000,
        "commission_normale": 2540, "commission_remise_max": 2190
    },
    15: {
        "panels": 36, "surface": 68,
        "prime": 2850, "tarif_rachat_surplus": 0.0761,
        "tarif_base_ht": 27200, "tarif_remise_ht": 26450, "tarif_remise_max_ht": 25700,
        "commission_normale": 2720, "commission_remise_max": 2345
    },
    16: {
        "panels": 38, "surface": 72,
        "prime": 3040, "tarif_rachat_surplus": 0.0761,
        "tarif_base_ht": 28900, "tarif_remise_ht": 28100, "tarif_remise_max_ht": 27300,
        "commission_normale": 2890, "commission_remise_max": 2490
    },
    17: {
        "panels": 40, "surface": 77,
        "prime": 3230, "tarif_rachat_surplus": 0.0761,
        "tarif_base_ht": 30600, "tarif_remise_ht": 29750, "tarif_remise_max_ht": 28900,
        "commission_normale": 3060, "commission_remise_max": 2635
    },
    18: {
        "panels": 43, "surface": 81,
        "prime": 3420, "tarif_rachat_surplus": 0.0761,
        "tarif_base_ht": 32200, "tarif_remise_ht": 31300, "tarif_remise_max_ht": 30400,
        "commission_normale": 3220, "commission_remise_max": 2770
    },
    19: {
        "panels": 45, "surface": 86,
        "prime": 3610, "tarif_rachat_surplus": 0.0761,
        "tarif_base_ht": 33900, "tarif_remise_ht": 32950, "tarif_remise_max_ht": 32000,
        "commission_normale": 3390, "commission_remise_max": 2915
    },
    20: {
        "panels": 48, "surface": 90,
        "prime": 3800, "tarif_rachat_surplus": 0.0761,
        "tarif_base_ht": 35600, "tarif_remise_ht": 34600, "tarif_remise_max_ht": 33600,
        "commission_normale": 3560, "commission_remise_max": 3060
    },
    21: {
        "panels": 50, "surface": 95,
        "prime": 3990, "tarif_rachat_surplus": 0.0761,
        "tarif_base_ht": 37200, "tarif_remise_ht": 36150, "tarif_remise_max_ht": 35100,
        "commission_normale": 3720, "commission_remise_max": 3195
    },
    22: {
        "panels": 52, "surface": 100,
        "prime": 4180, "tarif_rachat_surplus": 0.0761,
        "tarif_base_ht": 38800, "tarif_remise_ht": 37700, "tarif_remise_max_ht": 36600,
        "commission_normale": 3880, "commission_remise_max": 3330
    },
    23: {
        "panels": 55, "surface": 104,
        "prime": 4370, "tarif_rachat_surplus": 0.0761,
        "tarif_base_ht": 40400, "tarif_remise_ht": 39250, "tarif_remise_max_ht": 38100,
        "commission_normale": 4040, "commission_remise_max": 3465
    },
    24: {
        "panels": 57, "surface": 109,
        "prime": 4560, "tarif_rachat_surplus": 0.0761,
        "tarif_base_ht": 42000, "tarif_remise_ht": 40800, "tarif_remise_max_ht": 39600,
        "commission_normale": 4200, "commission_remise_max": 3600
    },
    25: {
        "panels": 60, "surface": 113,
        "prime": 4750, "tarif_rachat_surplus": 0.0761,
        "tarif_base_ht": 43600, "tarif_remise_ht": 42350, "tarif_remise_max_ht": 41100,
        "commission_normale": 4360, "commission_remise_max": 3735
    },
    26: {
        "panels": 62, "surface": 118,
        "prime": 4940, "tarif_rachat_surplus": 0.0761,
        "tarif_base_ht": 45200, "tarif_remise_ht": 43900, "tarif_remise_max_ht": 42600,
        "commission_normale": 4520, "commission_remise_max": 3870
    },
    27: {
        "panels": 64, "surface": 122,
        "prime": 5130, "tarif_rachat_surplus": 0.0761,
        "tarif_base_ht": 46700, "tarif_remise_ht": 45350, "tarif_remise_max_ht": 44000,
        "commission_normale": 4670, "commission_remise_max": 3995
    },
    28: {
        "panels": 67, "surface": 127,
        "prime": 5320, "tarif_rachat_surplus": 0.0761,
        "tarif_base_ht": 48300, "tarif_remise_ht": 46900, "tarif_remise_max_ht": 45500,
        "commission_normale": 4830, "commission_remise_max": 4130
    },
    29: {
        "panels": 69, "surface": 131,
        "prime": 5510, "tarif_rachat_surplus": 0.0761,
        "tarif_base_ht": 49800, "tarif_remise_ht": 48350, "tarif_remise_max_ht": 46900,
        "commission_normale": 4980, "commission_remise_max": 4255
    },
    30: {
        "panels": 71, "surface": 136,
        "prime": 5700, "tarif_rachat_surplus": 0.0761,
        "tarif_base_ht": 51300, "tarif_remise_ht": 49800, "tarif_remise_max_ht": 48300,
        "commission_normale": 5130, "commission_remise_max": 4380
    },
    31: {
        "panels": 74, "surface": 140,
        "prime": 5890, "tarif_rachat_surplus": 0.0761,
        "tarif_base_ht": 52900, "tarif_remise_ht": 51350, "tarif_remise_max_ht": 49800,
        "commission_normale": 5290, "commission_remise_max": 4515
    },
    32: {
        "panels": 76, "surface": 145,
        "prime": 6080, "tarif_rachat_surplus": 0.0761,
        "tarif_base_ht": 54300, "tarif_remise_ht": 52700, "tarif_remise_max_ht": 51100,
        "commission_normale": 5430, "commission_remise_max": 4650
    },
    33: {
        "panels": 79, "surface": 149,
        "prime": 6270, "tarif_rachat_surplus": 0.0761,
        "tarif_base_ht": 55800, "tarif_remise_ht": 54150, "tarif_remise_max_ht": 52500,
        "commission_normale": 5580, "commission_remise_max": 4755
    },
    34: {
        "panels": 81, "surface": 154,
        "prime": 6460, "tarif_rachat_surplus": 0.0761,
        "tarif_base_ht": 57300, "tarif_remise_ht": 55600, "tarif_remise_max_ht": 53900,
        "commission_normale": 5730, "commission_remise_max": 4880
    },
    35: {
        "panels": 83, "surface": 158,
        "prime": 6650, "tarif_rachat_surplus": 0.0761,
        "tarif_base_ht": 58800, "tarif_remise_ht": 57050, "tarif_remise_max_ht": 55300,
        "commission_normale": 5880, "commission_remise_max": 5005
    },
    36: {
        "panels": 86, "surface": 163,
        "prime": 6840, "tarif_rachat_surplus": 0.0761,
        "tarif_base_ht": 60200, "tarif_remise_ht": 58400, "tarif_remise_max_ht": 56600,
        "commission_normale": 6020, "commission_remise_max": 5120
    }
}

# Deprecated - keeping for backward compatibility
SOLAR_KITS = SOLAR_KITS_PARTICULIERS

# Matrice des taux de leasing professionnel
LEASING_MATRIX = {
    # Tranches de montant (min, max) : {durée_mois: taux}
    (12501, 25000): {
        60: 2.07,
        72: None,  # Zone rouge - non disponible
        84: None,  # Zone rouge - non disponible
        96: None   # Zone rouge - non disponible
    },
    (25001, 37500): {
        60: 2.06,
        72: 1.77,
        84: None,  # Zone rouge - non disponible
        96: None   # Zone rouge - non disponible
    },
    (37501, 50000): {
        60: 2.05,
        72: 1.76,
        84: 1.56,
        96: None   # Zone rouge - non disponible
    },
    (50001, 75000): {
        60: 2.04,
        72: 1.75,
        84: 1.55,
        96: 1.4
    },
    (75001, 100000): {
        60: 2.03,
        72: 1.74,
        84: 1.54,
        96: 1.39
    },
    (100001, 999999): {  # 100.000€ et +
        60: 2.02,
        72: 1.73,
        84: 1.53,
        96: 1.38
    }
}

def get_leasing_rate(amount: float, duration_months: int) -> float:
    """
    Get leasing rate based on amount and duration
    Returns None if combination is not available (zone rouge)
    """
    for (min_amount, max_amount), rates in LEASING_MATRIX.items():
        if min_amount <= amount <= max_amount:
            return rates.get(duration_months)
    return None

def calculate_leasing_options(amount: float) -> List[Dict]:
    """
    Calculate all available leasing options for an amount
    """
    options = []
    durations = [60, 72, 84, 96]
    
    for duration in durations:
        rate = get_leasing_rate(amount, duration)
        if rate is not None:  # Only if not in red zone
            monthly_payment = amount * (rate / 100)  # Convert percentage to decimal
            options.append({
                "duration_months": duration,
                "duration_years": duration / 12,
                "rate": rate,
                "monthly_payment": round(monthly_payment, 2),
                "total_payment": round(monthly_payment * duration, 2)
            })
    
    return options

def find_optimal_leasing_kit(solar_kits: dict, monthly_savings: float, client_mode: str = "professionnels") -> Dict:
    """
    Find the optimal kit that matches monthly savings with leasing payment
    Returns the "MEILLEUR KITS OPTIMISE"
    """
    if client_mode != "professionnels":
        return None
    
    best_options = []
    
    for power, kit_info in solar_kits.items():
        # Test all 3 price levels for professionals
        price_levels = {
            "base": kit_info.get('tarif_base_ht', 0),
            "remise": kit_info.get('tarif_remise_ht', 0),
            "remise_max": kit_info.get('tarif_remise_max_ht', 0)
        }
        
        for level, price in price_levels.items():
            if price > 0:
                leasing_options = calculate_leasing_options(price)
                
                for option in leasing_options:
                    monthly_payment = option['monthly_payment']
                    benefit = monthly_savings - monthly_payment
                    
                    # Only consider options where leasing payment <= monthly savings
                    if benefit >= 0:
                        best_options.append({
                            "kit_power": power,
                            "price_level": level,
                            "kit_price": price,
                            "duration_months": option['duration_months'],
                            "monthly_payment": monthly_payment,
                            "monthly_savings": monthly_savings,
                            "monthly_benefit": benefit,
                            "total_payment": option['total_payment'],
                            "leasing_rate": option['rate'],
                            "kit_info": kit_info
                        })
    
    # Sort by monthly benefit (highest first, then by lowest monthly payment)
    best_options.sort(key=lambda x: (-x['monthly_benefit'], x['monthly_payment']))
    
    return best_options[0] if best_options else None

# EDF rates and constants
EDF_RATE_PER_KWH = 0.2516  # €/kWh pour particuliers
EDF_RATE_PER_KWH_PROFESSIONNELS = 0.26  # €/kWh pour professionnels (autoconsommation)
ANNUAL_RATE_INCREASE = 0.05  # 5% per year
SURPLUS_SALE_RATE = 0.076  # €/kWh for surplus sold to EDF (particuliers)
SURPLUS_SALE_RATE_PROFESSIONNELS = 0.0761  # €/kWh for surplus sold to EDF (professionnels)

# Autoconsumption rates
AUTOCONSUMPTION_RATE_PARTICULIERS = 0.95  # 95% autoconsommation
AUTOCONSUMPTION_RATE_PROFESSIONNELS = 0.80  # 80% autoconsommation

# Aides et subventions - Particuliers
AUTOCONSUMPTION_AID_PARTICULIERS = 80  # €/kW installed
TVA_RATE_PARTICULIERS = 0.20  # 20% TVA (except 3kW)

# Aides et subventions - Professionnels
AUTOCONSUMPTION_AID_PROFESSIONNELS = 190  # €/kW installed (190€ par kW)
TVA_RATE_PROFESSIONNELS = 0.20  # 20% TVA mais amortissement différent
AMORTISSEMENT_ACCELERE = 0.30  # 30% amortissement accéléré première année

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

def get_solar_kits_by_mode(client_mode: str = "particuliers"):
    """
    Get solar kits based on client mode
    """
    if client_mode == "professionnels":
        return SOLAR_KITS_PROFESSIONNELS
    else:
        return SOLAR_KITS_PARTICULIERS

def get_professional_kit_price(kit_info: dict, price_level: str = "base") -> float:
    """
    Get professional kit price based on price level
    price_level: "base", "remise", "remise_max"
    """
    if price_level == "remise":
        return kit_info.get('tarif_remise_ht', kit_info.get('tarif_base_ht', 0))
    elif price_level == "remise_max":
        return kit_info.get('tarif_remise_max_ht', kit_info.get('tarif_base_ht', 0))
    else:  # base
        return kit_info.get('tarif_base_ht', 0)

def get_professional_commission(kit_info: dict, price_level: str = "base") -> float:
    """
    Get professional commission based on price level
    """
    if price_level == "remise_max":
        return kit_info.get('commission_remise_max', kit_info.get('commission_normale', 0))
    else:  # base or remise
        return kit_info.get('commission_normale', 0)

def get_aids_by_mode(client_mode: str = "particuliers"):
    """
    Get aids configuration based on client mode
    """
    if client_mode == "professionnels":
        return {
            "autoconsumption_aid_rate": AUTOCONSUMPTION_AID_PROFESSIONNELS,
            "tva_rate": TVA_RATE_PROFESSIONNELS,
            "amortissement_accelere": AMORTISSEMENT_ACCELERE,
            "autoconsumption_rate": AUTOCONSUMPTION_RATE_PROFESSIONNELS,
            "edf_rate": EDF_RATE_PER_KWH_PROFESSIONNELS,
            "surplus_sale_rate": SURPLUS_SALE_RATE_PROFESSIONNELS
        }
    else:
        return {
            "autoconsumption_aid_rate": AUTOCONSUMPTION_AID_PARTICULIERS,
            "tva_rate": TVA_RATE_PARTICULIERS,
            "amortissement_accelere": 0,
            "autoconsumption_rate": AUTOCONSUMPTION_RATE_PARTICULIERS,
            "edf_rate": EDF_RATE_PER_KWH,
            "surplus_sale_rate": SURPLUS_SALE_RATE
        }

def calculate_optimal_kit_size(annual_consumption: float, roof_surface: float, client_mode: str = "particuliers") -> int:
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
    
    # Find the closest available kit based on client mode
    available_kits = get_solar_kits_by_mode(client_mode)
    available_powers = list(available_kits.keys())
    best_power = min(available_powers, key=lambda x: abs(x - target_power))
    
    return best_power

def calculate_financing_options(kit_price: float, monthly_savings: float) -> List[Dict]:
    """
    Calculate financing options from 6 to 15 years
    """
    taeg = 0.0496  # 4.96% TAEG
    monthly_rate = taeg / 12
    options = []
    
    for years in range(6, 16):  # 6 to 15 years
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
            "difference_vs_savings": round(monthly_payment - monthly_savings, 2)
        })
    
    return options

def calculate_financing_with_aids(kit_price: float, total_aids: float, monthly_savings: float) -> Dict:
    """
    Calculate financing options with aids deducted - WITH INTERESTS
    """
    taeg = 0.0325  # 3.25% TAEG (taux réduit avec aides)
    monthly_rate = taeg / 12
    
    # Amount to finance after aids
    financed_amount = kit_price - total_aids
    
    # Calculate for 15 years (180 months) as shown in the screenshot
    years = 15
    months = years * 12
    
    if monthly_rate > 0:
        # Standard loan calculation WITH INTERESTS
        monthly_payment_with_interests = financed_amount * (monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)
    else:
        monthly_payment_with_interests = financed_amount / months
    
    return {
        "duration_years": years,
        "duration_months": months,
        "financed_amount": round(financed_amount, 2),
        "monthly_payment": round(monthly_payment_with_interests, 2),
        "total_interests": round((monthly_payment_with_interests * months) - financed_amount, 2),
        "difference_vs_savings": round(monthly_payment_with_interests - monthly_savings, 2)
    }

def calculate_all_financing_with_aids(kit_price: float, total_aids: float, monthly_savings: float) -> List[Dict]:
    """
    Calculate financing options with aids deducted for all durations (6-15 years) - WITH INTERESTS
    """
    taeg = 0.0325  # 3.25% TAEG (taux réduit avec aides)
    monthly_rate = taeg / 12
    
    # Amount to finance after aids
    financed_amount = kit_price - total_aids
    
    options = []
    
    for years in range(6, 16):  # 6 to 15 years
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
            "difference_vs_savings": round(monthly_payment_with_interests - monthly_savings, 2)
        })
    
    return options

# Routes
@api_router.get("/")
async def root():
    return {"message": "Solar Calculator API with PVGIS Integration"}

@api_router.get("/solar-kits")
async def get_solar_kits():
    """Get available solar kits with pricing (legacy endpoint for particuliers)"""
    return SOLAR_KITS_PARTICULIERS

@api_router.get("/solar-kits/{client_mode}")
async def get_solar_kits_by_client_mode(client_mode: str):
    """Get available solar kits with pricing based on client mode"""
    if client_mode not in ["particuliers", "professionnels"]:
        raise HTTPException(status_code=400, detail="Invalid client mode. Use 'particuliers' or 'professionnels'")
    
    return get_solar_kits_by_mode(client_mode)

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

@api_router.post("/calculate-professional/{client_id}")
async def calculate_professional_solution(client_id: str, price_level: str = "base"):
    """
    Calculate solar solution for professional clients with pricing level
    price_level: "base", "remise", "remise_max"
    """
    try:
        client = await db.clients.find_one({"id": client_id})
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Extract client data
        annual_consumption = client['annual_consumption_kwh']
        roof_surface = client['roof_surface']
        orientation = client['roof_orientation']
        lat = client['latitude']
        lon = client['longitude']
        client_mode = client.get('client_mode', 'professionnels')
        
        # Get appropriate kits and aids configuration
        solar_kits = get_solar_kits_by_mode(client_mode)
        aids_config = get_aids_by_mode(client_mode)
        
        # Calculate optimal kit size
        best_kit = calculate_optimal_kit_size(annual_consumption, roof_surface, client_mode)
        kit_info = solar_kits[best_kit]
        
        # Get price based on level for professionals
        if client_mode == "professionnels":
            kit_price = get_professional_kit_price(kit_info, price_level)
            commission = get_professional_commission(kit_info, price_level)
        else:
            kit_price = kit_info.get('price', 0)
            commission = 0
        
        # Get PVGIS data
        pvgis_data = await get_pvgis_data(lat, lon, orientation, best_kit)
        annual_production = pvgis_data["annual_production"]
        
        # Calculate autonomy percentage
        autonomy_percentage = min(95, (annual_production / annual_consumption) * 100)
        
        # Calculate autoconsumption with correct rates by mode
        autoconsumption_rate = aids_config['autoconsumption_rate']
        edf_rate = aids_config['edf_rate']
        surplus_sale_rate = aids_config['surplus_sale_rate']
        
        autoconsumption_kwh = annual_production * autoconsumption_rate
        surplus_kwh = annual_production * (1 - autoconsumption_rate)
        
        # Calculate savings with correct rates
        annual_savings = (autoconsumption_kwh * edf_rate) + (surplus_kwh * surplus_sale_rate)
        monthly_savings = annual_savings / 12
        
        # Calculate aids based on client mode
        if client_mode == "professionnels":
            # Pour les professionnels, utiliser la prime déjà calculée dans les kits
            autoconsumption_aid_total = kit_info.get('prime', 0)
            tva_refund = 0  # Pas de TVA pour les professionnels (récupérée par l'entreprise)
        else:
            # Pour les particuliers, calculer avec le taux habituel
            autoconsumption_aid_total = best_kit * aids_config['autoconsumption_aid_rate']
            tva_refund = kit_price * aids_config['tva_rate'] if best_kit > 3 else 0
        
        total_aids = autoconsumption_aid_total + tva_refund
        
        # Calculate financing options based on client mode
        if client_mode == "professionnels":
            # Pour les professionnels : utiliser le leasing
            leasing_options = calculate_leasing_options(kit_price)
            
            # Trouver le MEILLEUR KITS OPTIMISE
            optimal_kit = find_optimal_leasing_kit(solar_kits, monthly_savings, client_mode)
            
            result = {
                "client_id": client_id,
                "client_mode": client_mode,
                "price_level": price_level,
                "kit_power": best_kit,
                "panel_count": kit_info['panels'],
                "surface": kit_info.get('surface', 0),
                "estimated_production": annual_production,
                "estimated_savings": annual_savings,
                "autonomy_percentage": autonomy_percentage,
                "monthly_savings": monthly_savings,
                "kit_price": kit_price,
                "commission": commission,
                "autoconsumption_kwh": autoconsumption_kwh,
                "surplus_kwh": surplus_kwh,
                "autoconsumption_aid": autoconsumption_aid_total,
                "tva_refund": tva_refund,
                "total_aids": total_aids,
                "leasing_options": leasing_options,
                "optimal_kit": optimal_kit,
                "pvgis_source": "Données source PVGIS Commission Européenne",
                "orientation": orientation,
                "coordinates": {"lat": lat, "lon": lon},
                "aids_config": aids_config,
                "pricing_options": {
                    "tarif_base_ht": kit_info.get('tarif_base_ht', 0),
                    "tarif_remise_ht": kit_info.get('tarif_remise_ht', 0),
                    "tarif_remise_max_ht": kit_info.get('tarif_remise_max_ht', 0),
                    "commission_normale": kit_info.get('commission_normale', 0),
                    "commission_remise_max": kit_info.get('commission_remise_max', 0)
                }
            }
        else:
            # Pour les particuliers : utiliser le crédit classique
            financing_with_aids = calculate_financing_with_aids(kit_price, total_aids, monthly_savings)
            all_financing_with_aids = calculate_all_financing_with_aids(kit_price, total_aids, monthly_savings)
            
            result = {
                "client_id": client_id,
                "client_mode": client_mode,
                "price_level": price_level,
                "kit_power": best_kit,
                "panel_count": kit_info['panels'],
                "surface": kit_info.get('surface', 0),
                "estimated_production": annual_production,
                "estimated_savings": annual_savings,
                "autonomy_percentage": autonomy_percentage,
                "monthly_savings": monthly_savings,
                "kit_price": kit_price,
                "commission": commission,
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
                "aids_config": aids_config
            }
        
        return result
        
    except Exception as e:
        logging.error(f"Professional calculation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/calculate/{client_id}")
async def calculate_solar_solution(client_id: str):
    try:
        client = await db.clients.find_one({"id": client_id})
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Extract client data
        annual_consumption = client['annual_consumption_kwh']
        roof_surface = client['roof_surface']
        orientation = client['roof_orientation']
        lat = client['latitude']
        lon = client['longitude']
        client_mode = client.get('client_mode', 'particuliers')  # Default to particuliers if not specified
        
        # Get appropriate kits and aids configuration
        solar_kits = get_solar_kits_by_mode(client_mode)
        aids_config = get_aids_by_mode(client_mode)
        
        # Calculate optimal kit size
        best_kit = calculate_optimal_kit_size(annual_consumption, roof_surface, client_mode)
        kit_info = solar_kits[best_kit]
        
        # Get PVGIS data
        pvgis_data = await get_pvgis_data(lat, lon, orientation, best_kit)
        annual_production = pvgis_data["annual_production"]
        
        # Calculate autonomy percentage
        autonomy_percentage = min(95, (annual_production / annual_consumption) * 100)
        
        # Calculate autoconsumption with correct rates by mode
        aids_config = get_aids_by_mode(client_mode)
        autoconsumption_rate = aids_config['autoconsumption_rate']
        edf_rate = aids_config['edf_rate']
        surplus_sale_rate = aids_config['surplus_sale_rate']
        
        autoconsumption_kwh = annual_production * autoconsumption_rate
        surplus_kwh = annual_production * (1 - autoconsumption_rate)
        
        # Calculate savings with correct rates
        annual_savings = (autoconsumption_kwh * edf_rate) + (surplus_kwh * surplus_sale_rate)
        monthly_savings = annual_savings / 12
        
        # Calculate financing options
        financing_options = calculate_financing_options(kit_info['price'], monthly_savings)
        
        # Calculate aids based on client mode
        aids_config = get_aids_by_mode(client_mode)
        
        if client_mode == "professionnels":
            # Pour les professionnels, utiliser la prime déjà calculée dans les kits
            autoconsumption_aid_total = kit_info.get('prime', 0)
            tva_refund = 0  # Pas de TVA pour les professionnels (récupérée par l'entreprise)
        else:
            # Pour les particuliers, calculer avec le taux habituel
            autoconsumption_aid_total = best_kit * aids_config['autoconsumption_aid_rate']
            tva_refund = kit_info['price'] * aids_config['tva_rate'] if best_kit > 3 else 0
        
        total_aids = autoconsumption_aid_total + tva_refund
        
        # Calculate financing options with aids deducted
        financing_with_aids = calculate_financing_with_aids(kit_info['price'], total_aids, monthly_savings)
        
        # Calculate all financing options with aids deducted for all durations
        all_financing_with_aids = calculate_all_financing_with_aids(kit_info['price'], total_aids, monthly_savings)
        
        calculation = SolarCalculation(
            client_id=client_id,
            kit_power=best_kit,
            panel_count=kit_info['panels'],
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
                "recommended_kit_power": best_kit,
                "estimated_production": annual_production,
                "estimated_savings": annual_savings,
                "pvgis_data": pvgis_data
            }}
        )
        
        # Add additional info for frontend
        result = calculation.dict()
        result.update({
            "client_mode": client_mode,
            "kit_price": kit_info['price'],
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
            "aids_config": aids_config  # Include aids configuration for frontend
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

@api_router.get("/generate-pdf/{client_id}")
async def generate_pdf_report(client_id: str):
    """Generate and download PDF report for client"""
    try:
        # Get client
        client = await db.clients.find_one({"id": client_id})
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Get calculation data - recalculate if needed
        calculation_response = await calculate_solar_solution(client_id)
        
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