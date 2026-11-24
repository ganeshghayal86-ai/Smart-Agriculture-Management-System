
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Crop, DiseaseDetection, IrrigationSchedule, SoilTest
from django.contrib import messages
from ai_assistant.services import analyze_leaf_image
from django.shortcuts import get_object_or_404
from decimal import Decimal, InvalidOperation
from datetime import date
from datetime import date, timedelta
from django.http import HttpResponse
from reportlab.pdfgen import canvas

import json
import urllib.request
import urllib.parse

# Main Dashboard
@login_required
def dashboard(request):
    return render(request, 'farm/dashboard.html')


# Add Crop
@login_required
def add_crop(request):
    if request.method == 'POST':
        crop = Crop(
            farmer=request.user,
            crop_name=request.POST['crop_name'],
            area=request.POST['area'],
            sowing_date=request.POST['sowing_date'],
            expected_harvest_date=request.POST['expected_harvest_date']
        )
        crop.save()
        return redirect('dashboard')

    return render(request, 'farm/add_crop.html')


# View Crops
@login_required
def view_crops(request):
    crops = Crop.objects.filter(farmer=request.user)
    return render(request, 'farm/view_crops.html', {'crops': crops})


# Edit Crop
@login_required
def edit_crop(request, id):
    crop = Crop.objects.get(id=id, farmer=request.user)

    if request.method == 'POST':
        crop.crop_name = request.POST['crop_name']
        crop.area = request.POST['area']
        crop.sowing_date = request.POST['sowing_date']
        crop.expected_harvest_date = request.POST['expected_harvest_date']
        crop.save()

        return redirect('view_crops')

    return render(request, 'farm/edit_crop.html', {'crop': crop})


# Delete Crop
@login_required
def delete_crop(request, id):
    crop = Crop.objects.get(id=id, farmer=request.user)

    if request.method == 'POST':
        crop.delete()
        return redirect('view_crops')

    return render(request, 'farm/delete_crop.html', {'crop': crop})


# Crop Recommendation
def crop_recommendation(request):
    recommendations = []
    crop_details = []
    land_area = None

    crop_info = {
        "Soybean": {
            "season": "Kharif",
            "water": "Medium",
            "soil": "Black, Well-drained soil"
        },
        "Cotton": {
            "season": "Kharif",
            "water": "Medium",
            "soil": "Black soil"
        },
        "Maize": {
            "season": "Kharif / Rabi / Summer",
            "water": "Medium",
            "soil": "Well-drained loamy soil"
        },
        "Groundnut": {
            "season": "Kharif",
            "water": "Medium",
            "soil": "Sandy loam, Red soil"
        },
        "Tur": {
            "season": "Kharif",
            "water": "Low to Medium",
            "soil": "Well-drained soil"
        },
        "Wheat": {
            "season": "Rabi",
            "water": "Medium",
            "soil": "Loamy, Black soil"
        },
        "Chickpea": {
            "season": "Rabi",
            "water": "Low",
            "soil": "Well-drained loamy soil"
        },
        "Jowar": {
            "season": "Rabi",
            "water": "Low",
            "soil": "Black soil"
        },
        "Summer Moong": {
            "season": "Summer",
            "water": "Medium",
            "soil": "Well-drained loamy soil"
        },
        "Fodder Maize": {
            "season": "Summer",
            "water": "Medium",
            "soil": "Well-drained soil"
        }
    }

    if request.method == "POST":
        soil = request.POST.get('soil_type')
        season = request.POST.get('season')
        water = request.POST.get('water')
        land_area = request.POST.get('land_area')

        if season == "Kharif":
            if soil == "Black":
                recommendations = ["Soybean", "Cotton", "Maize"]
            else:
                recommendations = ["Maize", "Groundnut", "Tur"]

        elif season == "Rabi":
            if soil == "Black":
                recommendations = ["Wheat", "Chickpea", "Jowar"]
            else:
                recommendations = ["Chickpea", "Jowar", "Wheat"]

        elif season == "Summer":
            recommendations = ["Summer Moong", "Fodder Maize"]

        if water == "Low":
            recommendations = [
                crop for crop in recommendations
                if crop in ["Jowar", "Tur", "Chickpea"]
            ]

        crop_details = [
            {"name": crop, **crop_info[crop]}
            for crop in recommendations
        ]

    return render(
        request,
        'farm/crop_recommendation.html',
        {
            'recommendations': recommendations,
            'crop_details': crop_details,
            'land_area': land_area
        }
    )




def weather_information(request):
    weather = None
    forecast = []
    advice = []
    irrigation_advice = ""
    error = ""

    conditions = {
        0: "Clear Sky ☀️",
        1: "Mainly Clear 🌤️",
        2: "Partly Cloudy ⛅",
        3: "Overcast ☁️",
        45: "Fog 🌫️",
        48: "Fog 🌫️",
        51: "Light Drizzle 🌦️",
        53: "Moderate Drizzle 🌧️",
        55: "Heavy Drizzle 🌧️",
        56: "Freezing Drizzle 🌧️",
        57: "Heavy Freezing Drizzle 🌧️",
        61: "Light Rain 🌧️",
        63: "Moderate Rain 🌧️",
        65: "Heavy Rain 🌧️",
        66: "Freezing Rain 🌧️",
        67: "Heavy Freezing Rain 🌧️",
        71: "Light Snow ❄️",
        73: "Moderate Snow ❄️",
        75: "Heavy Snow ❄️",
        77: "Snow Grains ❄️",
        80: "Rain Showers 🌦️",
        81: "Moderate Rain Showers 🌧️",
        82: "Heavy Rain Showers 🌧️",
        85: "Snow Showers ❄️",
        86: "Heavy Snow Showers ❄️",
        95: "Thunderstorm ⛈️",
        96: "Thunderstorm with Hail ⛈️",
        99: "Heavy Thunderstorm ⛈️"
    }

    if request.method == "POST":
        city = request.POST.get('city', '').strip()

        try:
            geo_url = (
                "https://geocoding-api.open-meteo.com/v1/search?"
                + urllib.parse.urlencode({
                    "name": city,
                    "count": 1,
                    "language": "en",
                    "format": "json"
                })
            )

            with urllib.request.urlopen(geo_url, timeout=10) as response:
                geo_data = json.loads(response.read().decode())

            if not geo_data.get('results'):
                raise ValueError("City not found.")

            location = geo_data['results'][0]
            latitude = location['latitude']
            longitude = location['longitude']

            params = {
                "latitude": latitude,
                "longitude": longitude,
                "current": (
                    "temperature_2m,relative_humidity_2m,"
                    "precipitation,weather_code"
                ),
                "daily": (
                    "temperature_2m_max,"
                    "temperature_2m_min,"
                    "precipitation_sum,"
                    "weather_code"
                ),
                "forecast_days": 7,
                "timezone": "auto"
            }

            weather_url = (
                "https://api.open-meteo.com/v1/forecast?"
                + urllib.parse.urlencode(params)
            )

            with urllib.request.urlopen(weather_url, timeout=10) as response:
                data = json.loads(response.read().decode())

            current = data['current']
            weather_code = current['weather_code']

            weather = {
                'city': location['name'],
                'temperature': current['temperature_2m'],
                'humidity': current['relative_humidity_2m'],
                'rainfall': current['precipitation'],
                'condition': conditions.get(
                    weather_code, "Unknown Condition"
                )
            }

            # Current Weather Advice

            if current['precipitation'] > 0:
                advice.append(
                    "Rain detected. Avoid unnecessary irrigation."
                )
            else:
                advice.append(
                    "No current rain. Check soil moisture before irrigation."
                )

            if current['temperature_2m'] > 35:
                advice.append(
                    "High temperature. Monitor crops for heat stress."
                )

            if current['relative_humidity_2m'] > 80:
                advice.append(
                    "High humidity. Monitor crops for fungal disease symptoms."
                )

            if not advice:
                advice.append(
                    "Weather conditions look normal. Continue regular crop monitoring."
                )

            # 7-Day Forecast

            daily = data['daily']
            total_rainfall = 0
            rainy_days = 0

            for i in range(len(daily['time'])):
                code = daily['weather_code'][i]
                rainfall = daily['precipitation_sum'][i] or 0

                total_rainfall += rainfall

                if rainfall >= 5:
                    rainy_days += 1

                forecast.append({
                    'date': daily['time'][i],
                    'max_temp': daily['temperature_2m_max'][i],
                    'min_temp': daily['temperature_2m_min'][i],
                    'rainfall': rainfall,
                    'condition': conditions.get(
                        code, "Unknown Condition"
                    )
                })

            # Smart Irrigation Recommendation

            if total_rainfall >= 10:
                irrigation_advice = (
                    "Rainfall is expected during the next 7 days. "
                    "Avoid unnecessary irrigation and check soil moisture regularly."
                )

            elif total_rainfall > 0:
                irrigation_advice = (
                    "Light rainfall is expected. "
                    "Check soil moisture before deciding to irrigate."
                )

            else:
                irrigation_advice = (
                    "No rainfall is expected in the next 7 days. "
                    "Check soil moisture and plan irrigation if required."
                )

        except Exception:
            weather = None
            forecast = []
            advice = []
            irrigation_advice = ""
            error = (
                "Weather information unavailable. "
                "Please check city name or try again."
            )

    return render(request, 'farm/weather.html', {
        'weather': weather,
        'forecast': forecast,
        'advice': advice,
        'irrigation_advice': irrigation_advice,
        'error': error
    })

@login_required
def disease_detection(request):
    if request.method == "POST":
        crop_name = request.POST.get('crop_name')
        leaf_image = request.FILES.get('leaf_image')

        if crop_name and leaf_image:
            try:
                disease_result = analyze_leaf_image(
                    leaf_image,
                    crop_name
                )

                leaf_image.seek(0)

                DiseaseDetection.objects.create(
                    farmer=request.user,
                    crop_name=crop_name,
                    leaf_image=leaf_image,
                    disease_name=disease_result
                )

                return render(request, 'farm/disease_detection.html', {
                    'success': True,
                    'disease_result': disease_result
                })

            except Exception:
                leaf_image.seek(0)

                DiseaseDetection.objects.create(
                    farmer=request.user,
                    crop_name=crop_name,
                    leaf_image=leaf_image,
                    disease_name="Analysis unavailable"
                )

                return render(request, 'farm/disease_detection.html', {
                    'error': 'AI analysis failed. Please try again.'
                })

    return render(request, 'farm/disease_detection.html')
@login_required
def disease_history(request):
    search = request.GET.get('search', '')

    history = DiseaseDetection.objects.filter(
        farmer=request.user
    ).order_by('-uploaded_at')

    if search:
        history = history.filter(crop_name__icontains=search)

    return render(request, 'farm/disease_history.html', {
        'history': history,
        'search': search
    })

@login_required
def delete_disease_history(request, id):
    record = DiseaseDetection.objects.get(
        id=id,
        farmer=request.user
    )

    if request.method == "POST":
        if record.leaf_image:
            record.leaf_image.delete(save=False)

        record.delete()
        return redirect('disease_history')

    return redirect('disease_history')




@login_required
def irrigation_dashboard(request):
    today = date.today()
    upcoming_limit = today + timedelta(days=3)

    schedules = IrrigationSchedule.objects.filter(
        farmer=request.user
    ).select_related('crop').order_by('irrigation_date')

    total_schedules = schedules.count()

    completed = schedules.filter(
        status='Completed'
    ).count()

    pending = schedules.filter(
        status='Scheduled'
    ).count()

    # Today's Irrigation
    today_schedules = schedules.filter(
        status='Scheduled',
        irrigation_date=today
    )

    # Upcoming Irrigation - Next 3 Days
    upcoming_schedules = schedules.filter(
        status='Scheduled',
        irrigation_date__gt=today,
        irrigation_date__lte=upcoming_limit
    )

    # Overdue Irrigation
    overdue_schedules = schedules.filter(
        status='Scheduled',
        irrigation_date__lt=today
    )

    context = {
        'schedules': schedules,
        'total_schedules': total_schedules,
        'completed': completed,
        'pending': pending,
        'today_schedules': today_schedules,
        'upcoming_schedules': upcoming_schedules,
        'overdue_schedules': overdue_schedules,
        'today': today
    }

    return render(
        request,
        'farm/irrigation_dashboard.html',
        context
    )



# Add Irrigation Schedule
@login_required
def add_irrigation(request):
    crops = Crop.objects.filter(farmer=request.user)
    error = ''

    if request.method == 'POST':
        try:
            crop = get_object_or_404(
                Crop,
                id=request.POST.get('crop'),
                farmer=request.user
            )

            irrigation_date = date.fromisoformat(
                request.POST.get('irrigation_date', '')
            )

            water_quantity = Decimal(
                request.POST.get('water_quantity', '0')
            )

            if water_quantity <= 0:
                raise ValueError

            IrrigationSchedule.objects.create(
                farmer=request.user,
                crop=crop,
                irrigation_date=irrigation_date,
                water_quantity=water_quantity,
                water_unit=request.POST.get('water_unit', 'Liters'),
                irrigation_method=request.POST.get('irrigation_method'),
                notes=request.POST.get('notes', '')
            )

            return redirect('irrigation_dashboard')

        except (InvalidOperation, ValueError, TypeError):
            error = 'Please enter valid irrigation details.'

    return render(request, 'farm/add_irrigation.html', {
        'crops': crops,
        'error': error
    })


# Irrigation History
@login_required
def irrigation_history(request):
    schedules = IrrigationSchedule.objects.filter(
        farmer=request.user
    ).select_related('crop').order_by('-irrigation_date')

    return render(request, 'farm/irrigation_history.html', {
        'schedules': schedules
    })


# Edit Irrigation Schedule
@login_required
def edit_irrigation(request, id):
    schedule = get_object_or_404(
        IrrigationSchedule,
        id=id,
        farmer=request.user
    )

    crops = Crop.objects.filter(farmer=request.user)
    error = ''

    if request.method == 'POST':
        try:
            crop = get_object_or_404(
                Crop,
                id=request.POST.get('crop'),
                farmer=request.user
            )

            quantity = Decimal(
                request.POST.get('water_quantity', '0')
            )

            if quantity <= 0:
                raise ValueError

            schedule.crop = crop
            schedule.irrigation_date = date.fromisoformat(
                request.POST.get('irrigation_date', '')
            )
            schedule.water_quantity = quantity
            schedule.water_unit = request.POST.get('water_unit', 'Liters')
            schedule.irrigation_method = request.POST.get('irrigation_method')
            schedule.status = request.POST.get('status', 'Scheduled')
            schedule.notes = request.POST.get('notes', '')
            schedule.save()

            return redirect('irrigation_dashboard')

        except (InvalidOperation, ValueError, TypeError):
            error = 'Please enter valid irrigation details.'

    return render(request, 'farm/edit_irrigation.html', {
        'schedule': schedule,
        'crops': crops,
        'error': error
    })


# Delete Irrigation Schedule
@login_required
def delete_irrigation(request, id):
    schedule = get_object_or_404(
        IrrigationSchedule,
        id=id,
        farmer=request.user
    )

    if request.method == 'POST':
        schedule.delete()

    return redirect('irrigation_dashboard')
# Soil Health Dashboard


@login_required
def soil_dashboard(request):

    tests = SoilTest.objects.filter(
        farmer=request.user
    ).order_by('-test_date')

    total_tests = tests.count()
    latest_test = tests.first()

    # Soil pH Analysis
    ph_status = None

    if latest_test:
        if latest_test.soil_ph < 7:
            ph_status = "Acidic Soil"
        elif latest_test.soil_ph == 7:
            ph_status = "Neutral Soil"
        else:
            ph_status = "Alkaline Soil"

    # Average pH
    average_ph = None

    if total_tests > 0:
        total_ph = sum(test.soil_ph for test in tests)
        average_ph = round(total_ph / total_tests, 2)

    # NPK Analysis - Latest Soil Test
    nitrogen = None
    phosphorus = None
    potassium = None

    if latest_test:
        nitrogen = latest_test.nitrogen
        phosphorus = latest_test.phosphorus
        potassium = latest_test.potassium

    context = {
        'tests': tests,
        'total_tests': total_tests,
        'latest_test': latest_test,
        'average_ph': average_ph,
        'ph_status': ph_status,
        'nitrogen': nitrogen,
        'phosphorus': phosphorus,
        'potassium': potassium,
    }

    return render(
        request,
        'farm/soil_dashboard.html',
        context
    )


@login_required
def soil_test_list(request):

    tests = SoilTest.objects.filter(
        farmer=request.user
    ).order_by('-test_date')

    context = {
        'tests': tests
    }

    return render(
        request,
        'farm/soil_test_list.html',
        context
    )
@login_required
def soil_test_detail(request, test_id):

    test = get_object_or_404(
        SoilTest,
        id=test_id,
        farmer=request.user
    )

    context = {
        'test': test
    }

    return render(
        request,
        'farm/soil_test_detail.html',
        context
    )
@login_required
def edit_soil_test(request, test_id):

    test = get_object_or_404(
        SoilTest,
        id=test_id,
        farmer=request.user
    )

    if request.method == 'POST':

        test_date = request.POST.get('test_date')
        soil_type = request.POST.get('soil_type')
        soil_ph = request.POST.get('soil_ph')
        nitrogen = request.POST.get('nitrogen')
        phosphorus = request.POST.get('phosphorus')
        potassium = request.POST.get('potassium')
        location = request.POST.get('location')
        notes = request.POST.get('notes')

        test.test_date = test_date
        test.soil_type = soil_type
        test.soil_ph = soil_ph
        test.nitrogen = nitrogen
        test.phosphorus = phosphorus
        test.potassium = potassium
        test.location = location
        test.notes = notes

        test.save()

        messages.success(request, "Soil Test Report Updated Successfully!")

        return redirect('soil_test_detail', test_id=test.id)

    return render(
        request,
        'farm/edit_soil_test.html',
        {'test': test}
    )
@login_required
def delete_soil_test(request, test_id):

    test = get_object_or_404(
        SoilTest,
        id=test_id,
        farmer=request.user
    )

    if request.method == 'POST':
        test.delete()

        messages.success(
            request,
            "Soil Test Report Deleted Successfully!"
        )

        return redirect('soil_test_list')

    return redirect('soil_test_detail', test_id=test.id)

@login_required
def download_soil_test_pdf(request, test_id):

    test = get_object_or_404(
        SoilTest,
        id=test_id,
        farmer=request.user
    )

    response = HttpResponse(
        content_type='application/pdf'
    )

    response['Content-Disposition'] = (
        f'attachment; filename="soil_test_report_{test.id}.pdf"'
    )

    p = canvas.Canvas(response)

    p.setTitle("Soil Test Report")

    p.setFont("Helvetica-Bold", 18)
    p.drawString(180, 800, "SOIL TEST REPORT")

    p.line(50, 785, 550, 785)

    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, 750, "Farmer Information")

    p.setFont("Helvetica", 11)
    p.drawString(50, 725, f"Farmer Name: {test.farmer}")
    p.drawString(50, 705, f"Test Date: {test.test_date}")
    p.drawString(50, 685, f"Location: {test.location or 'Not Available'}")

    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, 645, "Soil Information")

    p.setFont("Helvetica", 11)
    p.drawString(50, 620, f"Soil Type: {test.soil_type}")
    p.drawString(50, 600, f"Soil pH: {test.soil_ph}")

    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, 560, "NPK Nutrient Information")

    p.setFont("Helvetica", 11)
    p.drawString(50, 535, f"Nitrogen (N): {test.nitrogen}")
    p.drawString(50, 515, f"Phosphorus (P): {test.phosphorus}")
    p.drawString(50, 495, f"Potassium (K): {test.potassium}")

    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, 455, "Additional Notes")

    p.setFont("Helvetica", 11)

    notes = test.notes or "No Notes Available"

    y = 430

    for line in notes.splitlines():
        p.drawString(50, y, line[:90])
        y -= 18

    p.line(50, 80, 550, 80)

    p.setFont("Helvetica", 9)
    p.drawString(50, 60, "Generated by Smart Agriculture System")

    p.save()

    return response

# Add Soil Test
@login_required
def add_soil_test(request):

    error = ''

    if request.method == 'POST':
        try:
            test_date = date.fromisoformat(
                request.POST.get('test_date', '')
            )

            soil_type = request.POST.get('soil_type', '').strip()
            soil_ph = Decimal(request.POST.get('soil_ph', ''))
            nitrogen = Decimal(request.POST.get('nitrogen', ''))
            phosphorus = Decimal(request.POST.get('phosphorus', ''))
            potassium = Decimal(request.POST.get('potassium', ''))

            if not soil_type:
                raise ValueError

            if soil_ph < 0 or soil_ph > 14:
                raise ValueError

            if nitrogen < 0 or phosphorus < 0 or potassium < 0:
                raise ValueError

            SoilTest.objects.create(
                farmer=request.user,
                test_date=test_date,
                soil_type=soil_type,
                soil_ph=soil_ph,
                nitrogen=nitrogen,
                phosphorus=phosphorus,
                potassium=potassium,
                location=request.POST.get('location', ''),
                notes=request.POST.get('notes', '')
            )

            return redirect('soil_dashboard')

        except (InvalidOperation, ValueError, TypeError):
            error = 'Please enter valid soil test details.'

    return render(request, 'farm/add_soil_test.html', {
        'error': error
    })