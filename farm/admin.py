
from django.contrib import admin
from .models import Crop, DiseaseDetection, IrrigationSchedule, SoilTest


admin.site.register(Crop)
admin.site.register(DiseaseDetection)
admin.site.register(IrrigationSchedule)
admin.site.register(SoilTest)
