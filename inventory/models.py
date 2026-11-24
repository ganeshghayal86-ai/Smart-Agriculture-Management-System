
from django.db import models
from django.conf import settings


class Inventory(models.Model):

    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    item_name = models.CharField(max_length=100)

    category = models.CharField(max_length=50)

    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    unit = models.CharField(max_length=20)

    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    purchase_date = models.DateField()

    description = models.TextField(blank=True)

    # Low Stock Alert Threshold
    low_stock_threshold = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=5.00
    )

    def is_low_stock(self):
        return self.quantity <= self.low_stock_threshold

    def __str__(self):
        return self.item_name


class InventoryUsage(models.Model):

    inventory = models.ForeignKey(
        Inventory,
        on_delete=models.CASCADE,
        related_name='usages'
    )

    quantity_used = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    usage_date = models.DateField()

    purpose = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.inventory.item_name} - {self.quantity_used}"
