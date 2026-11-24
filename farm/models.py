from django.db import models
from django.conf import settings

class Crop(models.Model):

    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    crop_name = models.CharField(max_length=100)
    area = models.DecimalField(max_digits=10, decimal_places=2)
    sowing_date = models.DateField()
    expected_harvest_date = models.DateField()

    status = models.CharField(
        max_length=30,
        default='Growing'
    )

    def __str__(self):
        return self.crop_name

class DiseaseDetection(models.Model):
    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    crop_name = models.CharField(max_length=100)
    leaf_image = models.ImageField(upload_to='disease_images/')
    disease_name = models.CharField(max_length=200, default='Not Detected')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.crop_name

class IrrigationSchedule(models.Model):

    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    crop = models.ForeignKey(
        Crop,
        on_delete=models.CASCADE
    )

    irrigation_date = models.DateField()

    water_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    water_unit = models.CharField(
        max_length=20,
        default='Liters'
    )

    irrigation_method = models.CharField(
        max_length=50,
        choices=[
            ('Drip', 'Drip Irrigation'),
            ('Sprinkler', 'Sprinkler Irrigation'),
            ('Flood', 'Flood Irrigation'),
            ('Other', 'Other')
        ]
    )

    notes = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        default='Scheduled',
        choices=[
            ('Scheduled', 'Scheduled'),
            ('Completed', 'Completed'),
            ('Cancelled', 'Cancelled')
        ]
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.crop.crop_name} - {self.irrigation_date}"

class SoilTest(models.Model):

    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    test_date = models.DateField()

    soil_type = models.CharField(
        max_length=100
    )

    soil_ph = models.DecimalField(
        max_digits=4,
        decimal_places=2
    )

    nitrogen = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    phosphorus = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    potassium = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    location = models.CharField(
        max_length=200,
        blank=True
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.farmer} - Soil Test - {self.test_date}"
