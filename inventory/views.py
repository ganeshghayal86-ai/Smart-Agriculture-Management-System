
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from decimal import Decimal, InvalidOperation
from datetime import date, datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)

from .models import Inventory, InventoryUsage


@login_required
def add_inventory(request):
    if request.method == 'POST':
        item = Inventory(
            farmer=request.user,
            item_name=request.POST['item_name'],
            category=request.POST['category'],
            quantity=request.POST['quantity'],
            unit=request.POST['unit'],
            purchase_price=request.POST['purchase_price'],
            purchase_date=request.POST['purchase_date'],
            description=request.POST.get('description', '')
        )
        item.save()
        return redirect('inventory_dashboard')

    return render(request, 'inventory/add_inventory.html')


@login_required
def inventory_dashboard(request):
    items = Inventory.objects.filter(farmer=request.user)
    total_items = items.count()
    total_value = sum(
        (item.quantity * item.purchase_price for item in items),
        Decimal('0')
    )
    low_stock_items = [item for item in items if item.is_low_stock()]

    context = {
        'items': items,
        'total_items': total_items,
        'total_value': total_value,
        'low_stock_items': low_stock_items
    }

    return render(request, 'inventory/dashboard.html', context)


@login_required
def edit_inventory(request, id):
    item = get_object_or_404(Inventory, id=id, farmer=request.user)

    if request.method == 'POST':
        item.item_name = request.POST['item_name']
        item.category = request.POST['category']
        item.quantity = request.POST['quantity']
        item.unit = request.POST['unit']
        item.purchase_price = request.POST['purchase_price']
        item.purchase_date = request.POST['purchase_date']
        item.description = request.POST.get('description', '')
        item.save()

        return redirect('inventory_dashboard')

    return render(request, 'inventory/edit_inventory.html', {'item': item})


@login_required
def delete_inventory(request, id):
    item = get_object_or_404(Inventory, id=id, farmer=request.user)

    if request.method == 'POST':
        item.delete()
        return redirect('inventory_dashboard')

    return render(request, 'inventory/delete_inventory.html', {'item': item})


@login_required
def add_inventory_usage(request):
    items = Inventory.objects.filter(farmer=request.user)
    error = ''

    if request.method == 'POST':
        try:
            inventory_id = request.POST.get('inventory')
            quantity_used = Decimal(request.POST.get('quantity_used', '0'))
            usage_date = date.fromisoformat(request.POST.get('usage_date', ''))
            purpose = request.POST.get('purpose', '').strip()
            description = request.POST.get('description', '')

            if quantity_used <= 0 or not purpose:
                raise ValueError

            with transaction.atomic():
                item = get_object_or_404(
                    Inventory.objects.select_for_update(),
                    id=inventory_id,
                    farmer=request.user
                )

                if quantity_used > item.quantity:
                    error = f'Available stock is only {item.quantity} {item.unit}.'
                else:
                    item.quantity -= quantity_used
                    item.save(update_fields=['quantity'])

                    InventoryUsage.objects.create(
                        inventory=item,
                        quantity_used=quantity_used,
                        usage_date=usage_date,
                        purpose=purpose,
                        description=description
                    )

                    return redirect('inventory_dashboard')

        except (InvalidOperation, ValueError, TypeError):
            error = 'Please enter valid usage details.'

    context = {
        'items': items,
        'error': error
    }

    return render(request, 'inventory/add_usage.html', context)


@login_required
def usage_history(request):
    usages = InventoryUsage.objects.filter(
        inventory__farmer=request.user
    ).select_related('inventory').order_by('-usage_date', '-created_at')

    return render(
        request,
        'inventory/usage_history.html',
        {'usages': usages}
    )


@login_required
def inventory_reports(request):
    items = Inventory.objects.filter(farmer=request.user)
    usages = InventoryUsage.objects.filter(
        inventory__farmer=request.user
    ).select_related('inventory')

    total_items = items.count()

    total_stock_value = sum(
        (item.quantity * item.purchase_price for item in items),
        Decimal('0')
    )

    total_quantity_used = sum(
        (usage.quantity_used for usage in usages),
        Decimal('0')
    )

    total_purchase_value = total_stock_value

    context = {
        'items': items,
        'usages': usages,
        'total_items': total_items,
        'total_stock_value': total_stock_value,
        'total_quantity_used': total_quantity_used,
        'total_purchase_value': total_purchase_value,
    }

    return render(request, 'inventory/reports.html', context)


@login_required
def download_inventory_pdf(request):
    items = Inventory.objects.filter(farmer=request.user)
    usages = InventoryUsage.objects.filter(
        inventory__farmer=request.user
    ).select_related('inventory').order_by('-usage_date')

    total_stock_value = sum(
        (item.quantity * item.purchase_price for item in items),
        Decimal('0')
    )

    total_quantity_used = sum(
        (usage.quantity_used for usage in usages),
        Decimal('0')
    )

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        'attachment; filename="inventory_report.pdf"'
    )

    document = SimpleDocTemplate(
        response,
        pagesize=landscape(A4),
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(
        "Smart Agriculture - Inventory Report",
        styles['Title']
    ))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(
        f"Farmer Name: {request.user.get_full_name() or request.user.username}",
        styles['Normal']
    ))
    elements.append(Paragraph(
        f"Report Date: {datetime.now().strftime('%d-%m-%Y')}",
        styles['Normal']
    ))
    elements.append(Spacer(1, 15))

    elements.append(Paragraph("Inventory Summary", styles['Heading2']))

    summary_data = [
        ['Total Items', 'Remaining Stock Value', 'Total Quantity Used'],
        [
            str(items.count()),
            f"Rs. {total_stock_value:.2f}",
            f"{total_quantity_used:.2f}"
        ]
    ]

    summary_table = Table(summary_data, colWidths=[2.5 * inch] * 3)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))

    elements.append(summary_table)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Item-wise Stock Report", styles['Heading2']))

    stock_data = [[
        'Item Name', 'Category', 'Quantity',
        'Unit', 'Price per Unit', 'Stock Value'
    ]]

    for item in items:
        stock_data.append([
            item.item_name,
            item.category,
            str(item.quantity),
            item.unit,
            f"Rs. {item.purchase_price:.2f}",
            f"Rs. {item.quantity * item.purchase_price:.2f}"
        ])

    stock_table = Table(stock_data, repeatRows=1)
    stock_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('PADDING', (0, 0), (-1, -1), 7),
    ]))

    elements.append(stock_table)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Inventory Usage History", styles['Heading2']))

    usage_data = [[
        'Item Name', 'Quantity Used', 'Unit', 'Date', 'Purpose'
    ]]

    for usage in usages:
        usage_data.append([
            usage.inventory.item_name,
            str(usage.quantity_used),
            usage.inventory.unit,
            str(usage.usage_date),
            usage.purpose
        ])

    usage_table = Table(usage_data, repeatRows=1)
    usage_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('PADDING', (0, 0), (-1, -1), 7),
    ]))

    elements.append(usage_table)

    document.build(elements)

    return response
