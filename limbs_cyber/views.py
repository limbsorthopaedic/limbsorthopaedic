
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Count, F
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json
from .models import ProductService, Sale, DailySummary
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from io import BytesIO


@staff_member_required
def cyber_pos_dashboard(request):
    """Main POS dashboard with statistics and quick sale entry"""
    today = timezone.now().date()
    
    # Today's statistics
    today_stats = Sale.get_daily_stats(today)
    
    # This week's statistics
    week_start = today - timedelta(days=today.weekday())
    week_stats = Sale.get_period_stats(week_start, today)
    
    # This month's statistics
    month_start = today.replace(day=1)
    month_stats = Sale.get_period_stats(month_start, today)
    
    # Get active products/services
    products = ProductService.objects.filter(is_active=True).order_by('name')
    
    # Recent sales (last 10)
    recent_sales = Sale.objects.select_related('product_service', 'staff').order_by('-sale_date')[:10]
    
    # Top selling items (this month)
    top_items = Sale.objects.filter(sale_date__date__gte=month_start)\
        .values('product_service__name')\
        .annotate(total_qty=Sum('quantity'), total_revenue=Sum('total_amount'))\
        .order_by('-total_revenue')[:5]
    
    # Daily revenue trend (last 7 days)
    daily_trend = []
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        day_sales = Sale.objects.filter(sale_date__date=date)
        revenue = sum(sale.total_amount for sale in day_sales)
        daily_trend.append({
            'date': date.strftime('%a, %b %d'),
            'revenue': float(revenue)
        })
    
    context = {
        'title': 'Limbs Cyber POS',
        'today_stats': today_stats,
        'week_stats': week_stats,
        'month_stats': month_stats,
        'products': products,
        'recent_sales': recent_sales,
        'top_items': top_items,
        'daily_trend': json.dumps(daily_trend),
    }
    
    return render(request, 'limbs_cyber/dashboard.html', context)


@staff_member_required
def create_sale(request):
    """Create a new sale transaction"""
    if request.method == 'POST':
        try:
            product_id = request.POST.get('product_service')
            quantity = int(request.POST.get('quantity', 1))
            customer_name = request.POST.get('customer_name', '')
            notes = request.POST.get('notes', '')
            
            product = get_object_or_404(ProductService, id=product_id, is_active=True)
            
            # Check stock
            if product.current_stock != 999 and product.current_stock < quantity:
                return JsonResponse({
                    'success': False,
                    'message': f'Insufficient stock. Only {product.current_stock} available.'
                })
            
            # Create sale
            sale = Sale.objects.create(
                product_service=product,
                unit_price=product.unit_price,
                quantity=quantity,
                customer_name=customer_name,
                staff=request.user,
                notes=notes
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Sale recorded successfully! Total: KSh {sale.total_amount:,.2f}',
                'transaction_number': sale.transaction_number
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@staff_member_required
def daily_report(request, date=None):
    """Generate daily sales report"""
    if date:
        report_date = datetime.strptime(date, '%Y-%m-%d').date()
    else:
        report_date = timezone.now().date()
    
    stats = Sale.get_daily_stats(report_date)
    sales = stats['sales']
    
    # Group by product/service
    product_summary = sales.values('product_service__name', 'product_service__unit_price')\
        .annotate(total_qty=Sum('quantity'), total_revenue=Sum('total_amount'))\
        .order_by('-total_revenue')
    
    context = {
        'title': f'Daily Report - {report_date}',
        'report_date': report_date,
        'stats': stats,
        'sales': sales,
        'product_summary': product_summary,
    }
    
    return render(request, 'limbs_cyber/daily_report.html', context)


@staff_member_required
def daily_report_pdf(request, date=None):
    """Generate PDF of daily sales report"""
    if date:
        report_date = datetime.strptime(date, '%Y-%m-%d').date()
    else:
        report_date = timezone.now().date()
    
    stats = Sale.get_daily_stats(report_date)
    sales = stats['sales']
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e266f'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    elements.append(Paragraph('LIMBS CYBER - DAILY SALES REPORT', title_style))
    elements.append(Paragraph(f'Report Date: {report_date.strftime("%B %d, %Y")}', styles['Normal']))
    elements.append(Spacer(1, 0.5*inch))
    
    # Summary
    summary_data = [
        ['Total Sales:', str(stats['total_sales'])],
        ['Total Items Sold:', str(stats['total_items'])],
        ['Total Revenue:', f"KSh {stats['total_revenue']:,.2f}"],
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Sales details
    if sales.exists():
        elements.append(Paragraph('Sales Transactions', styles['Heading2']))
        elements.append(Spacer(1, 0.2*inch))
        
        sales_data = [['Time', 'Product/Service', 'Qty', 'Unit Price', 'Total', 'Customer']]
        
        for sale in sales:
            sales_data.append([
                sale.sale_date.strftime('%H:%M'),
                sale.product_service.name,
                str(sale.quantity),
                f"KSh {sale.unit_price:,.2f}",
                f"KSh {sale.total_amount:,.2f}",
                sale.customer_name or '-'
            ])
        
        sales_table = Table(sales_data, colWidths=[0.8*inch, 2.5*inch, 0.5*inch, 1*inch, 1*inch, 1.5*inch])
        sales_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(sales_table)
    
    # Payment info
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph('Payment Method: M-Pesa Pochi la Biashara - 0708581688', styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="limbs_cyber_report_{report_date}.pdf"'
    
    return response


@staff_member_required
def generate_receipt(request, sale_id):
    """Generate receipt for a specific sale"""
    sale = get_object_or_404(Sale, id=sale_id)
    
    # Create PDF receipt
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Header
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1e266f'),
        alignment=TA_CENTER
    )
    
    elements.append(Paragraph('LIMBS CYBER', header_style))
    elements.append(Paragraph('ICIPE Road, Kasarani, Nairobi, Kenya', styles['Normal']))
    elements.append(Paragraph('Phone: +254 708 581 688', styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph('RECEIPT', styles['Heading2']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Receipt details
    receipt_data = [
        ['Transaction #:', sale.transaction_number],
        ['Date:', sale.sale_date.strftime('%B %d, %Y %H:%M')],
        ['Customer:', sale.customer_name or 'Walk-in Customer'],
        ['Served by:', sale.staff.get_full_name() if sale.staff else 'Staff'],
    ]
    
    receipt_table = Table(receipt_data, colWidths=[2*inch, 4*inch])
    receipt_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ]))
    
    elements.append(receipt_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Item details
    item_data = [
        ['Item', 'Quantity', 'Unit Price', 'Total'],
        [
            sale.product_service.name,
            str(sale.quantity),
            f"KSh {sale.unit_price:,.2f}",
            f"KSh {sale.total_amount:,.2f}"
        ]
    ]
    
    item_table = Table(item_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
    item_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ]))
    
    elements.append(item_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Total
    total_style = ParagraphStyle(
        'Total',
        parent=styles['Normal'],
        fontSize=14,
        fontName='Helvetica-Bold',
        alignment=TA_RIGHT
    )
    elements.append(Paragraph(f'TOTAL: KSh {sale.total_amount:,.2f}', total_style))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(f'Payment: {sale.payment_method}', styles['Normal']))
    
    # Footer
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph('Thank you for your business!', styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    # Update receipt status
    sale.receipt_generated = True
    sale.save()
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{sale.transaction_number}.pdf"'
    
    return response
