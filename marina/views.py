from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse, HttpResponse
from .utils import render_to_pdf
from .models import Berth, Booking, Customer, Invoice, Block, Boat
from .forms import BookingForm, CustomerForm, BoatForm

def quick_boat_create(request):
    if request.method == 'POST':
        c_form = CustomerForm(request.POST)
        b_form = BoatForm(request.POST)
        if c_form.is_valid() and b_form.is_valid():
            customer = c_form.save()
            boat = b_form.save(commit=False)
            boat.owner = customer
            boat.save()
            # Return just the ID so JS can select it
            return HttpResponse(f'<script>selectNewBoat("{boat.id}", "{boat.name}");</script>')
    else:
        c_form = CustomerForm()
        b_form = BoatForm()
    
    return render(request, 'marina/partials/quick_boat_form.html', {
        'c_form': c_form,
        'b_form': b_form
    })

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
    
    # Calculate estimated price (Berth Fee)
    berth_fee = booking.calculate_price()
    
    # Calculate service costs
    from .models import BookingService, InvoiceItem
    booked_services = booking.services.all()
    service_total = sum(s.total_price for s in booked_services)
    
    total_price = berth_fee + service_total
    
    if request.method == 'POST':
        # Finalize checkout
        booking.status = 'COMPLETED'
        booking.end_date = timezone.now().date()
        booking.save()
        
        # Create Invoice
        invoice = Invoice.objects.create(
            customer=booking.boat.owner,
            booking=booking,
            total_amount=total_price,
            status='OPEN'
        )
        
        # Add primary line item (Berth Fee)
        InvoiceItem.objects.create(
            invoice=invoice,
            description=f"Berth Fee: {booking.boat.name} ({booking.boat.length}m) for {booking.duration_days} days",
            quantity=booking.duration_days,
            unit_price=berth_fee / booking.duration_days if booking.duration_days > 0 else 0
        )
        
        # Add service line items
        for bs in booked_services:
            InvoiceItem.objects.create(
                invoice=invoice,
                description=f"Service: {bs.service.name}",
                quantity=bs.quantity,
                unit_price=bs.service.price
            )
        
        return render(request, 'marina/partials/checkout_success.html', {'invoice': invoice})

    return render(request, 'marina/partials/checkout_confirm.html', {
        'booking': booking,
        'total_price': total_price,
        'berth_fee': berth_fee,
        'service_total': service_total,
        'booked_services': booked_services
    })

def booking_edit(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            return HttpResponse('<script>window.location.reload();</script>')
    else:
        form = BookingForm(instance=booking)
    return render(request, 'marina/partials/booking_form.html', {'form': form, 'editing': True})

def booking_delete(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == 'POST':
        booking.delete()
        return HttpResponse('<script>window.location.reload();</script>')
    return render(request, 'marina/partials/booking_delete_confirm.html', {'booking': booking})

def add_service(request, booking_id):
    from .models import BookingService, Service
    booking = get_object_or_404(Booking, id=booking_id)
    services = Service.objects.all()
    
    if request.method == 'POST':
        service_id = request.POST.get('service')
        quantity = float(request.POST.get('quantity', 1))
        service = get_object_or_404(Service, id=service_id)
        
        BookingService.objects.create(
            booking=booking,
            service=service,
            quantity=quantity
        )
        return HttpResponse('<script>window.location.reload();</script>')
        
    return render(request, 'marina/partials/add_service_form.html', {
        'booking': booking,
        'services': services
    })

def invoice_pdf(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    context = {
        'invoice': invoice,
        'block_color': invoice.booking.berth.block.color if invoice.booking else '#3498db'
    }
    return render_to_pdf('marina/invoice_pdf.html', context)

def dashboard(request):
    from django.utils import timezone
    today = timezone.now().date()
    berths_count = Berth.objects.count()
    active_bookings = Booking.objects.filter(status='ACTIVE').count()
    customers_count = Customer.objects.count()
    # Block Stats for Visual Layout
    blocks = Block.objects.all().order_by('name')
    block_labels = [b.name for b in blocks]
    block_colors = [b.color for b in blocks]
    block_stats = []
    block_occupancy = []
    
    for b in blocks:
        total = b.berths.count()
        occupied = Booking.objects.filter(berth__block=b, status='ACTIVE').count()
        block_stats.append({
            'name': b.name,
            'color': b.color,
            'total': total,
            'occupied': occupied,
            'vacant': total - occupied,
            'percent': int((occupied / total * 100)) if total > 0 else 0
        })
        block_occupancy.append(occupied)
    
    # All Berths with Occupancy for Schematic Map
    all_berths = []
    for berth in Berth.objects.all().select_related('block'):
        booking = Booking.objects.filter(
            berth=berth, 
            start_date__lte=today, 
            end_date__gte=today,
            status='ACTIVE'
        ).first()
        
        # Calculate Schematic Position (Docked to piers)
        num = int(berth.number)
        x, y = 0, 0
        if berth.block.name == 'A':
            x, y = 150 + (num * 30), 125
        elif berth.block.name == 'B':
            x, y = 100 + (num * 35), 295
        elif berth.block.name == 'C':
            x, y = 100 + (num * 35), 370
        elif berth.block.name == 'D':
            x, y = 50 + (num * 40), 595
        elif berth.block.name == 'E':
            x, y = 820, 150 + (num * 30)
            
        all_berths.append({
            'obj': berth,
            'booking': booking,
            'x': x,
            'y': y,
            'boat_name': booking.boat.name if booking else '',
            'owner': booking.boat.owner.name if booking else '',
            'length': booking.boat.length if booking else '',
            'start': booking.start_date.strftime('%d.%m.%Y') if booking else '',
            'end': booking.end_date.strftime('%d.%m.%Y') if booking else '',
            'flag': booking.boat.flag if booking else '',
        })
    
    context = {
        'berths_count': berths_count,
        'active_bookings': active_bookings,
        'customers_count': customers_count,
        'block_labels': block_labels,
        'block_colors': block_colors,
        'block_occupancy': block_occupancy,
        'block_stats': block_stats,
        'all_berths': all_berths,
    }
    return render(request, 'marina/dashboard.html', context)

def calendar_view(request):
    return render(request, 'marina/calendar.html')

def berths_grid(request):
    blocks = Block.objects.all().order_by('name')
    return render(request, 'marina/berths_grid.html', {'blocks': blocks})

def invoices_list(request):
    invoices = Invoice.objects.all().prefetch_related('items', 'customer').order_by('-date')
    return render(request, 'marina/invoices_list.html', {'invoices': invoices})

def invoice_mark_paid(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    invoice.status = 'PAID'
    invoice.save()
    return redirect('invoices_list')

def invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        invoice.delete()
        return redirect('invoices_list')
    return render(request, 'marina/partials/invoice_delete_confirm.html', {'invoice': invoice})

def customers_list(request):
    customers = Customer.objects.all().prefetch_related('boats').order_by('name')
    return render(request, 'marina/customers_list.html', {'customers': customers})

def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customers_list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'marina/partials/customer_form_modal.html', {'form': form, 'customer': customer})

def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        return redirect('customers_list')
    return render(request, 'marina/partials/customer_delete_confirm.html', {'customer': customer})

def boat_edit(request, pk):
    boat = get_object_or_404(Boat, pk=pk)
    if request.method == 'POST':
        form = BoatForm(request.POST, request.FILES, instance=boat)
        if form.is_valid():
            form.save()
            if request.headers.get('HX-Request'):
                from django.http import HttpResponse
                response = HttpResponse()
                response['HX-Trigger'] = 'boatChanged'
                return response
            return redirect('customers_list')
    else:
        form = BoatForm(instance=boat)
    return render(request, 'marina/partials/boat_form_modal.html', {'form': form, 'boat': boat})

def boat_delete(request, pk):
    boat = get_object_or_404(Boat, pk=pk)
    if request.method == 'POST':
        boat.delete()
        return redirect('customers_list')
    return render(request, 'marina/partials/boat_delete_confirm.html', {'boat': boat})

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
                'block': berth.block.name,
                'block_color': berth.block.color,
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
    from .models import Block, Berth
    blocks = Block.objects.all().order_by('name')
    berths = Berth.objects.all().select_related('block').order_by('block__name', 'number')
    
    resources = []
    # Add Blocks as parent groups
    for block in blocks:
        resources.append({
            'id': f"block_{block.id}",
            'content': f"{block.name}",
            'nestedGroups': [b.id for b in block.berths.all()],
            'className': 'bg-light fw-bold'
        })
        
    # Add Berths as child groups
    for berth in berths:
        resources.append({
            'id': berth.id,
            'content': f"Berth {berth.number}",
        })
        
    return JsonResponse(resources, safe=False)

def api_events(request):
    start = request.GET.get('start')
    end = request.GET.get('end')
    
    # Filter bookings that overlap with the visible range
    bookings = Booking.objects.all().select_related('boat', 'berth', 'berth__block')
    
    if start and end:
        # DayPilot sends ISO strings (YYYY-MM-DDTHH:mm:ss), we need YYYY-MM-DD for DateField
        clean_start = start[:10]
        clean_end = end[:10]
        bookings = bookings.filter(start_date__lt=clean_end, end_date__gt=clean_start)
    
    events = []
    for b in bookings:
        events.append({
            'id': b.id,
            'text': f"{b.boat.name}",
            'start': b.start_date.isoformat(),
            'end': b.end_date.isoformat(),
            'resource': b.berth.id,
            'type': b.booking_type,
            'is_at_sea': b.is_at_sea,
            'color': b.boat.color,
            'flag': b.boat.flag.lower(),
            'owner': b.boat.owner.name,
            'boat_type': b.boat.get_boat_type_display(),
            'length': b.boat.length
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
            'block': berth.block.name,
            'block_id': berth.block.id,
            'number': berth.number,
            'max_length': berth.max_length,
            'max_weight': berth.max_weight,
            'current_boat': current_booking.boat.name if current_booking else 'None',
            'owner': current_booking.boat.owner.name if current_booking else 'None',
            'owner_email': current_booking.boat.owner.email if current_booking else '',
            'flag': current_booking.boat.owner.nationality.lower() if current_booking else '',
            'check_in': current_booking.start_date.strftime('%d.%m.') if current_booking else '',
            'check_out': current_booking.end_date.strftime('%d.%m.') if current_booking else '',
            'boat_type': current_booking.boat.boat_type if current_booking else '',
            'boat_image': current_booking.boat.image.url if current_booking and current_booking.boat.image else '/static/img/default-boat.png',
            'boat_id': current_booking.boat.id if current_booking else None,
            'booking_id': current_booking.id if current_booking else None,
            'status': status
        })
    return JsonResponse(data, safe=False)
