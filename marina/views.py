from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse, HttpResponse
from .utils import render_to_pdf
from .models import Berth, Booking, Customer, Invoice
from .forms import BookingForm

def booking_create(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.status = 'ACTIVE'
            booking.save()
            return HttpResponse('<script>window.location.reload();</script>')
    else:
        initial = {
            'start_date': request.GET.get('start'),
            'end_date': request.GET.get('end'),
            'berth': request.GET.get('resource'),
        }
        form = BookingForm(initial=initial)
    
    return render(request, 'marina/partials/booking_form.html', {'form': form})

def checkout_view(request, berth_id):
    from django.utils import timezone
    berth = get_object_or_404(Berth, id=berth_id)
    booking = Booking.objects.filter(berth=berth, status='ACTIVE').first()
    
    if not booking:
        return HttpResponse("No active booking found for this berth.")
    
    if request.method == 'POST':
        # Finalize checkout
        booking.status = 'COMPLETED'
        booking.end_date = timezone.now().date()
        booking.save()
        
        # Create Invoice
        amount = booking.calculate_price()
        invoice = Invoice.objects.create(
            customer=booking.boat.owner,
            booking=booking,
            total_amount=amount,
            status='OPEN'
        )
        # Add basic item
        from .models import InvoiceItem
        InvoiceItem.objects.create(
            invoice=invoice,
            description=f"Berth Fee for {booking.boat.name} ({booking.duration_days} days)",
            quantity=1,
            unit_price=amount
        )
        
        return render(request, 'marina/partials/checkout_success.html', {'invoice': invoice})

    return render(request, 'marina/partials/checkout_confirm.html', {'booking': booking})

def invoice_pdf(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    context = {'invoice': invoice}
    return render_to_pdf('marina/invoice_pdf.html', context)

def dashboard(request):
    berths_count = Berth.objects.count()
    active_bookings = Booking.objects.filter(status='ACTIVE').count()
    customers_count = Customer.objects.count()
    berths = Berth.objects.all()
    
    context = {
        'berths_count': berths_count,
        'active_bookings': active_bookings,
        'customers_count': customers_count,
        'berths': berths,
    }
    return render(request, 'marina/dashboard.html', context)

def calendar_view(request):
    return render(request, 'marina/calendar.html')

def berths_grid(request):
    return render(request, 'marina/berths_grid.html')

def invoices_list(request):
    invoices = Invoice.objects.all().order_by('-date')
    return render(request, 'marina/invoices_list.html', {'invoices': invoices})

def customers_list(request):
    customers = Customer.objects.all()
    return render(request, 'marina/customers_list.html', {'customers': customers})

def planning_grid(request):
    return render(request, 'marina/planning_grid.html')

def reports_view(request):
    from django.db.models import Sum, Count, Avg
    from django.db.models.functions import TruncMonth
    
    # Revenue by Month
    revenue_data = Invoice.objects.filter(status='PAID').annotate(
        month=TruncMonth('date')
    ).values('month').annotate(total=Sum('total_amount')).order_by('month')
    
    # Occupancy by Block
    berths_total = Berth.objects.count()
    active_bookings = Booking.objects.filter(status='ACTIVE').count()
    occupancy_rate = (active_bookings / berths_total * 100) if berths_total > 0 else 0
    
    # Top Customers
    top_customers = Customer.objects.annotate(
        total_spent=Sum('invoices__total_amount')
    ).order_by('-total_spent')[:5]
    
    # Average Boat Size
    avg_boat_length = Boat.objects.aggregate(Avg('length'))['length__avg']
    
    context = {
        'revenue_data': list(revenue_data),
        'occupancy_rate': round(occupancy_rate, 1),
        'top_customers': top_customers,
        'avg_boat_length': round(avg_boat_length, 1) if avg_boat_length else 0,
    }
    return render(request, 'marina/reports.html', context)

def api_planning_data(request):
    import datetime
    year = int(request.GET.get('year', datetime.date.today().year))
    
    start_date = datetime.date(year, 1, 1)
    end_date = datetime.date(year + 1, 12, 31) # Current + Following year
    
    # Pre-fetch all bookings for the period
    bookings = Booking.objects.filter(
        start_date__lte=end_date,
        end_date__gte=start_date
    ).select_related('boat', 'berth')
    
    berths = Berth.objects.all()
    data = []
    
    # Create a lookup dictionary for bookings: {(berth_id, date): booking}
    booking_lookup = {}
    for b in bookings:
        curr_b = b.start_date
        while curr_b <= b.end_date:
            booking_lookup[(b.berth_id, curr_b)] = b
            curr_b += datetime.timedelta(days=1)
    
    berths = Berth.objects.all()
    data = []
    
    # Iterate through each day and each berth
    curr = start_date
    while curr <= end_date:
        for berth in berths:
            booking = booking_lookup.get((berth.id, curr))
            
            row = {
                'date': curr.isoformat(),
                'block': berth.block,
                'berth': berth.number,
                'boat_name': booking.boat.name if booking else '-',
                'flag': booking.boat.flag if booking else '-',
                'arrival': booking.start_date.isoformat() if booking else '-',
                'departure': booking.end_date.isoformat() if booking else '-',
                'days': booking.duration_days if booking else '-',
                'status': 'Occupied' if booking else 'Vacant',
            }
            if booking and booking.is_at_sea:
                row['status'] = 'At Sea'
                
            data.append(row)
        curr += datetime.timedelta(days=1)
        
    return JsonResponse(data, safe=False)

def api_resources(request):
    blocks = Berth.objects.values_list('block', flat=True).distinct().order_by('block')
    resources = []
    for block in blocks:
        children = []
        for berth in Berth.objects.filter(block=block).order_by('number'):
            children.append({
                'name': f"Berth {berth.number}",
                'id': berth.id
            })
        resources.append({
            'name': f"Block {block}",
            'id': f"B_{block}",
            'expanded': True,
            'children': children
        })
    return JsonResponse(resources, safe=False)

def api_events(request):
    start = request.GET.get('start')
    end = request.GET.get('end')
    bookings = Booking.objects.all()
    if start and end:
        bookings = bookings.filter(start_date__lt=end, end_date__gt=start)
    
    events = []
    for b in bookings:
        events.append({
            'id': b.id,
            'text': f"{b.boat.name} ({b.boat.flag})",
            'start': b.start_date.isoformat(),
            'end': b.end_date.isoformat(),
            'resource': b.berth.id,
            'type': b.booking_type,
            'is_at_sea': b.is_at_sea,
            'color': '#3498db' if b.booking_type == 'LONG' else '#e67e22'
        })
    return JsonResponse(events, safe=False)

def api_berths(request):
    from django.utils import timezone
    today = timezone.now().date()
    berths = Berth.objects.all()
    data = []
    for berth in berths:
        current_booking = Booking.objects.filter(
            berth=berth, 
            start_date__lte=today, 
            end_date__gte=today,
            status='ACTIVE'
        ).first()
        
        status = 'Vacant'
        if current_booking:
            if current_booking.is_at_sea:
                status = 'At Sea (Sub-lease Available)'
            else:
                status = 'Occupied'
        
        data.append({
            'id': berth.id,
            'block': berth.block,
            'number': berth.number,
            'max_length': berth.max_length,
            'max_weight': berth.max_weight,
            'current_boat': current_booking.boat.name if current_booking else 'None',
            'status': status
        })
    return JsonResponse(data, safe=False)
