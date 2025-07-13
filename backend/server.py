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
            "total_cost": round(monthly_payment * months, 2),
            "savings_ratio": round(savings_ratio, 2),
            "difference_vs_savings": round(monthly_payment - monthly_savings, 2)
        })
    
    return options

def calculate_financing_with_aids(kit_price: float, total_aids: float, monthly_savings: float) -> Dict:
    """
    Calculate financing options with aids deducted - WITH INTERESTS
    """
    taeg = 0.0496  # 4.96% TAEG
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
        "total_cost": round(monthly_payment_with_interests * months, 2),
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
            "total_cost": round(monthly_payment_with_interests * months, 2),
            "total_interests": round((monthly_payment_with_interests * months) - financed_amount, 2),
            "difference_vs_savings": round(monthly_payment_with_interests - monthly_savings, 2)
        })
    
    return options

# Routes
@api_router.get("/")
async def root():
    return {"message": "Solar Calculator API with PVGIS Integration"}

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
        
        # Calculate optimal kit size
        best_kit = calculate_optimal_kit_size(annual_consumption, roof_surface)
        kit_info = SOLAR_KITS[best_kit]
        
        # Get PVGIS data
        pvgis_data = await get_pvgis_data(lat, lon, orientation, best_kit)
        annual_production = pvgis_data["annual_production"]
        
        # Calculate autonomy percentage
        autonomy_percentage = min(95, (annual_production / annual_consumption) * 100)
        
        # Calculate autoconsumption (assuming 70% of production is self-consumed)
        autoconsumption_rate = 0.7
        autoconsumption_kwh = annual_production * autoconsumption_rate
        surplus_kwh = annual_production * (1 - autoconsumption_rate)
        
        # Calculate savings
        annual_savings = (autoconsumption_kwh * EDF_RATE_PER_KWH) + (surplus_kwh * SURPLUS_SALE_RATE)
        monthly_savings = annual_savings / 12
        
        # Calculate financing options
        financing_options = calculate_financing_options(kit_info['price'], monthly_savings)
        
        # Calculate aids
        autoconsumption_aid_total = best_kit * AUTOCONSUMPTION_AID  # 80€/kW
        tva_refund = kit_info['price'] * TVA_RATE if best_kit > 3 else 0  # No TVA refund for 3kW
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
            "coordinates": {"lat": lat, "lon": lon}
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
            finance_data = [['Durée', 'Mensualité', 'Coût total', 'Économie mensuelle', 'Différence']]
            
            for option in calculation_data['financing_options'][:5]:  # Show first 5 options
                difference = option['difference_vs_savings']
                diff_text = f"+{difference:.0f} €" if difference > 0 else f"{difference:.0f} €"
                finance_data.append([
                    f"{option['duration_years']} ans",
                    f"{option['monthly_payment']:.0f} €",
                    f"{option['total_cost']:,.0f} €",
                    f"{calculation_data['monthly_savings']:.0f} €",
                    diff_text
                ])
            
            finance_table = Table(finance_data, colWidths=[2.5*cm, 2.5*cm, 3*cm, 3*cm, 3*cm])
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