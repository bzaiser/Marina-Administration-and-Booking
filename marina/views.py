from django.db import models
from django.db.models import Sum, Count, Q, Avg
from django.db.models.functions import Length
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from .utils import render_to_pdf
from .models import Berth, Booking, Customer, Invoice, Block, Boat, InvoiceItem, Service, ServiceProvider, WorkOrder, WorkOrderItem, BookingSupply
from .forms import BookingForm, CustomerForm, BoatForm, InvoiceForm, InvoiceItemForm, WorkOrderForm, WorkOrderItemForm, BookingSupplyForm
from .mydata_utils import send_invoice_to_mydata
from django.contrib import messages

@login_required
def quick_boat_create(request):
    start = request.GET.get('start', '')
    end = request.GET.get('end', '')
    berth = request.GET.get('berth', '')
    next_view = request.GET.get('next_view', 'booking_create')
    
    if request.method == 'POST':
        start = request.POST.get('orig_start', '')
        end = request.POST.get('orig_end', '')
        berth = request.POST.get('orig_berth', '')
        next_view = request.POST.get('next_view', 'booking_create')
        c_form = CustomerForm(request.POST, request.FILES, prefix='c')
        b_form = BoatForm(request.POST, request.FILES, prefix='b')
        if c_form.is_valid() and b_form.is_valid():
            customer = c_form.save()
            boat = b_form.save(commit=False)
            boat.owner = customer
            boat.save()
            from django.shortcuts import redirect
            from django.urls import reverse
            if next_view == 'work_order_create':
                url = f"{reverse('work_order_create')}?boat_id={boat.id}"
            else:
                url = f"{reverse('booking_create')}?start={start}&end={end}&resource={berth}&boat={boat.id}"
            return redirect(url)
    else:
        c_form = CustomerForm(prefix='c')
        b_form = BoatForm(prefix='b')
    
    template = 'marina/partials/quick_boat_form.html'
    if not request.htmx:
        template = 'marina/full_page_modal.html'
    
    return render(request, template, {
        'c_form': c_form,
        'b_form': b_form,
        'orig_start': start,
        'orig_end': end,
        'orig_berth': berth,
        'next_view': next_view,
        'partial_template': 'marina/partials/quick_boat_form.html',
        'title': 'New Boat Registration'
    })

@login_required
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
            'boat': request.GET.get('boat'),
        }
        form = BookingForm(initial=initial)
    
    template = 'marina/partials/booking_form.html'
    if not request.htmx:
        template = 'marina/full_page_modal.html'

    return render(request, template, {
        'form': form,
        'partial_template': 'marina/partials/booking_form.html',
        'title': 'Create Booking'
    })

@login_required
def checkout_view(request, berth_id):
    from django.utils import timezone
    berth = get_object_or_404(Berth, id=berth_id)
    booking = Booking.objects.filter(berth=berth, status='ACTIVE').first()
    
    if not booking:
        return HttpResponse("No active booking found for this berth.")
    
    # Calculate estimated price (Berth Fee)
    berth_fee = booking.calculate_price()
    
    # Calculate supply costs (Marina World)
    supplies = booking.supplies.all()
    supply_total = sum(s.total_price for s in supplies)
    
    # Calculate related Work Orders (Yard World) - Optionally included or just listed
    work_orders = WorkOrder.objects.filter(boat=booking.boat, status='COMPLETED') # Only bill completed work?
    work_total = 0
    for order in work_orders:
        for item in order.items.all():
            work_total += item.total_price
    
    total_price = berth_fee + supply_total + work_total
    
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
            unit='DAY',
            unit_price=berth_fee / booking.duration_days if booking.duration_days > 0 else 0
        )
        
        # Add supply line items
        for supply in supplies:
            InvoiceItem.objects.create(
                invoice=invoice,
                description=f"Supply: {supply.service.name}",
                quantity=supply.quantity,
                unit=supply.service.unit,
                unit_price=supply.unit_price or supply.service.price_per_unit
            )

        # Add work order line items (if any)
        for order in work_orders:
            for item in order.items.all():
                InvoiceItem.objects.create(
                    invoice=invoice,
                    description=f"Yard Work: {item.service.name}",
                    quantity=item.quantity,
                    unit=item.service.unit,
                    unit_price=item.unit_price or item.service.price_per_unit
                )
        
        return redirect('invoice_edit', pk=invoice.id)

    template = 'marina/partials/checkout_confirm.html'
    if not request.htmx:
        template = 'marina/checkout_confirm_full.html'

    # Prepare a combined list of services for the confirmation modal
    booked_services = []
    for s in supplies:
        booked_services.append({'service': s.service, 'quantity': s.quantity, 'total_price': s.total_price})
    for order in work_orders:
        for item in order.items.all():
            booked_services.append({'service': item.service, 'quantity': item.quantity, 'total_price': item.total_price})

    return render(request, template, {
        'booking': booking,
        'total_price': total_price,
        'berth_fee': berth_fee,
        'supply_total': supply_total,
        'work_total': work_total,
        'booked_services': booked_services
    })


@login_required
def booking_edit(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            if request.htmx:
                return HttpResponse('<script>window.location.reload();</script>')
            return redirect('bookings_list')
    else:
        form = BookingForm(instance=booking)
    
    supplies = booking.supplies.all().select_related('service')
    supply_form = BookingSupplyForm()
    all_services = Service.objects.filter(category__is_for_marina=True).order_by('name')
    
    template = 'marina/partials/booking_form.html'
    if not request.htmx:
        template = 'marina/full_page_modal.html'

    return render(request, template, {
        'form': form, 
        'editing': True,
        'booking': booking,
        'supplies': supplies,
        'supply_form': supply_form,
        'all_services': all_services,
        'partial_template': 'marina/partials/booking_form.html',
        'title': f'Edit Booking #{booking.id}'
    })

@login_required
@login_required
def booking_add_supply(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == 'POST':
        # Also save header if present in request
        header_form = BookingForm(request.POST, instance=booking)
        if header_form.is_valid():
            header_form.save()

        service_id = request.POST.get('service')
        quantity = float(request.POST.get('quantity', 1))
        if service_id:
            service = get_object_or_404(Service, id=service_id)
            BookingSupply.objects.create(
                booking=booking,
                service=service,
                quantity=quantity
            )
            
    if request.htmx:
        form = BookingForm(instance=booking)
        supplies = booking.supplies.all()
        all_services = Service.objects.filter(category__is_for_marina=True).order_by('name')
        return render(request, 'marina/partials/booking_form.html', {
            'form': form,
            'supplies': supplies,
            'all_services': all_services,
            'editing': True,
            'booking': booking
        })
    return redirect('bookings_list')

@login_required
def booking_remove_supply(request, supply_id):
    supply = get_object_or_404(BookingSupply, id=supply_id)
    booking = supply.booking
    
    if request.method == 'POST':
        # Also save header if present in request
        header_form = BookingForm(request.POST, instance=booking)
        if header_form.is_valid():
            header_form.save()
            
    supply.delete()
    
    if request.htmx:
        form = BookingForm(instance=booking)
        supplies = booking.supplies.all()
        all_services = Service.objects.filter(category__is_for_marina=True).order_by('name')
        return render(request, 'marina/partials/booking_form.html', {
            'form': form,
            'supplies': supplies,
            'all_services': all_services,
            'editing': True,
            'booking': booking
        })
    return redirect('bookings_list')

@login_required
def work_order_list(request):
    orders = WorkOrder.objects.all().order_by('-date_created')
    return render(request, 'marina/work_order_list.html', {'orders': orders})

@login_required
def work_order_edit(request, order_id):
    order = get_object_or_404(WorkOrder, id=order_id)
    if request.method == 'POST':
        form = WorkOrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return HttpResponse(status=204, headers={'HX-Trigger': 'planningDataChanged'})
    else:
        form = WorkOrderForm(instance=order)
    
    all_services = Service.objects.filter(category__is_for_yard=True).order_by('name')
    return render(request, 'marina/modals/work_order_form.html', {
        'form': form,
        'order': order,
        'editing': True,
        'title': 'Edit Work Order',
        'all_services': all_services
    })

@login_required
def work_order_add_item(request, order_id):
    order = get_object_or_404(WorkOrder, id=order_id)
    if request.method == 'POST':
        service_id = request.POST.get('add_service_id')
        raw_quantity = request.POST.get('add_quantity', '1')
        
        try:
            quantity = float(raw_quantity) if raw_quantity else 1.0
        except ValueError:
            quantity = 1.0
            
        if service_id:
            service = get_object_or_404(Service, id=service_id)
            WorkOrderItem.objects.create(
                order=order,
                service=service,
                quantity=quantity
            )
    
    all_services = Service.objects.filter(category__is_for_yard=True).order_by('name')
    return render(request, 'marina/partials/work_order_items_table.html', {
        'order': order,
        'all_services': all_services
    })

@login_required
def work_order_remove_item(request, item_id):
    item = get_object_or_404(WorkOrderItem, id=item_id)
    order = item.order
    item.delete()
    
    all_services = Service.objects.filter(category__is_for_yard=True).order_by('name')
    return render(request, 'marina/partials/work_order_items_table.html', {
        'order': order,
        'all_services': all_services
    })

@login_required
@login_required
def work_order_delete(request, order_id):
    order = get_object_or_404(WorkOrder, id=order_id)
    if request.method == 'POST':
        order.delete()
        return HttpResponse(status=204, headers={'HX-Trigger': 'planningDataChanged'})
    return render(request, 'marina/modals/work_order_delete_confirm.html', {'order': order})

@login_required
def work_order_checkout(request, order_id):
    order = get_object_or_404(WorkOrder, id=order_id)
    
    # Create Invoice
    invoice = Invoice.objects.create(
        customer=order.customer or order.boat.owner,
        total_amount=order.total_value,
        status='OPEN'
    )
    
    # Add items to invoice
    for item in order.items.all():
        InvoiceItem.objects.create(
            invoice=invoice,
            description=f"Yard Work: {item.service.name}",
            quantity=item.quantity,
            unit=item.service.unit,
            unit_price=item.unit_price or item.service.price_per_unit
        )
    
    # Mark order as completed
    order.status = 'COMPLETED'
    order.save()
    
    return redirect('invoice_edit', pk=invoice.id)

def work_order_create(request):
    boat_id = request.GET.get('boat_id')
    initial = {}
    if boat_id:
        initial['boat'] = boat_id
        boat = Boat.objects.filter(id=boat_id).first()
        if boat:
            initial['customer'] = boat.owner_id
    
    if request.method == 'POST':
        form = WorkOrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            
            # Create initial item if provided
            initial_service = form.cleaned_data.get('initial_service')
            initial_qty = form.cleaned_data.get('initial_quantity') or 1.0
            if initial_service:
                WorkOrderItem.objects.create(
                    order=order,
                    service=initial_service,
                    quantity=initial_qty
                )
            
            action = request.POST.get('action')
            if action == 'edit':
                from django.shortcuts import redirect
                response = redirect('work_order_edit', order_id=order.id)
                response['HX-Trigger'] = 'planningDataChanged'
                return response
                
            return HttpResponse(status=204, headers={'HX-Trigger': 'planningDataChanged'})
    else:
        form = WorkOrderForm(initial=initial)
    
    all_services = Service.objects.filter(category__is_for_yard=True).order_by('name')
    return render(request, 'marina/modals/work_order_form.html', {
        'form': form,
        'title': 'Create Work Order',
        'all_services': all_services
    })

@login_required
def booking_delete(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == 'POST':
        booking.delete()
        return HttpResponse('<script>window.location.reload();</script>')
    return render(request, 'marina/partials/booking_delete_confirm.html', {'booking': booking})

def add_service(request, booking_id):
    from .models import ServiceOrder, ServiceOrderItem, Service, Invoice, InvoiceItem
    booking = get_object_or_404(Booking, id=booking_id)
    services = Service.objects.all().order_by('name')
    
    if request.method == 'POST':
        service_id = request.POST.get('service')
        quantity = float(request.POST.get('quantity', 1))
        price_override = request.POST.get('price_per_unit')
        notes = request.POST.get('notes', '')
        
        service = get_object_or_404(Service, id=service_id)
        final_price = float(price_override) if price_override else service.price_per_unit
        
        # Create a ServiceOrder header first
        order = ServiceOrder.objects.create(
            booking=booking,
            boat=booking.boat,
            customer=booking.boat.owner,
            berth=booking.berth,
            status='PENDING',
            notes=f"Added from booking #{booking.id}"
        )
        
        # Create the item within that order
        item = ServiceOrderItem.objects.create(
            order=order,
            service=service,
            quantity=quantity,
            price_per_unit=final_price,
            notes=notes
        )
        
        # If the booking has an existing invoice, add the item to it and reset status to OPEN
        invoice = Invoice.objects.filter(booking=booking).first()
        if invoice:
            InvoiceItem.objects.create(
                invoice=invoice,
                description=f"Service: {service.name}",
                quantity=quantity,
                unit=service.unit,
                unit_price=final_price
            )
            invoice.status = 'OPEN'
            invoice.recalculate_total()
            
        return HttpResponse('<script>window.location.reload();</script>')
        
    template = 'marina/partials/add_service_form.html'
    if not request.htmx:
        template = 'marina/full_page_modal.html'

    return render(request, template, {
        'booking': booking,
        'services': services,
        'partial_template': 'marina/partials/add_service_form.html',
        'title': 'Add Service'
    })

@login_required
def invoice_pdf(request, invoice_id):
    import base64
    import os
    invoice = get_object_or_404(Invoice, id=invoice_id)
    invoice.recalculate_total() # Ensure total is correct
    
    # Embed logo as base64 for reliability
    logo_path = os.path.join(settings.BASE_DIR, 'media', 'logo.jpg')
    logo_base64 = ""
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as image_file:
            logo_base64 = base64.b64encode(image_file.read()).decode('utf-8')
    
    context = {
        'invoice': invoice,
        'logo_base64': logo_base64,
        'block_color': invoice.booking.berth.block.color if invoice.booking else '#3498db'
    }
    return render_to_pdf('marina/invoice_pdf.html', context)

@login_required
def dashboard(request):
    from django.utils import timezone
    today = timezone.now().date()
    berths_count = Berth.objects.count()
    active_bookings = Booking.objects.filter(
        status='ACTIVE',
        start_date__lte=today,
        end_date__gte=today
    ).count()
    customers_count = Customer.objects.count()
    # Block Stats for Visual Layout
    blocks = Block.objects.all().order_by('name')
    block_labels = [b.name for b in blocks]
    block_colors = [b.color for b in blocks]
    block_stats = []
    block_occupancy = []
    
    total_percent = int((active_bookings / berths_count * 100)) if berths_count > 0 else 0
    
    for b in blocks:
        total = b.berths.count()
        occupied = Booking.objects.filter(
            berth__block=b, 
            status='ACTIVE',
            start_date__lte=today,
            end_date__gte=today
        ).count()
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
    # Organize berths by block, sorting numerically
    import re
    block_berths = {}
    berths = list(Berth.objects.all().select_related('block'))
    
    def berth_sort_key(b):
        m = re.search(r'(\d+)', b.number)
        num = int(m.group(1)) if m else 0
        return (b.block.name, num, b.number)
        
    berths.sort(key=berth_sort_key)
    
    for berth in berths:
        if berth.block.name not in block_berths:
            block_berths[berth.block.name] = []
        block_berths[berth.block.name].append(berth)
        
    # Centerline start, end, rotation angle, and L_short (rectangle width) for each block's polygon
    import math
    segments = {
        'A': ((236.4, 163.0), (661.7, 126.3), -4.9, 94.3),
        'B': ((280.0, 356.3), (686.4, 218.5), -18.7, 92.2),
        'C': ((325.1, 477.8), (729.1, 335.0), -19.4, 89.2),
        'D': ((257.2, 738.0), (738.7, 577.4), -18.4, 100.0),
        'E': ((949.1, 426.7), (947.6, 808.9), 90.0, 115.0)
    }

    for block_name, b_list in block_berths.items():
        # Get the capacity of the block. We assume at least 15 slots, 
        # or more if the highest berth number is higher.
        max_num = 0
        for b in b_list:
            m = re.search(r'(\d+)', b.number)
            if m:
                max_num = max(max_num, int(m.group(1)))
        
        # This allows for dynamic blocks but keeps positions fixed if a middle berth is deleted.
        # It also handles blocks with more than 15 berths.
        total_slots = max(15, max_num)
        
        # Use the block's 'key' or 'name' from the first berth in this group
        first_berth = b_list[0]
        lookup_key = (first_berth.block.key or first_berth.block.name).strip()
        
        for idx, berth in enumerate(b_list):
            booking = Booking.objects.filter(
                berth=berth, 
                start_date__lte=today, 
                end_date__gte=today,
                status='ACTIVE'
            ).first()
            
            # Interpolate position and calculate dimensions
            x, y, rot = 0, 0, 0
            w, h = 15, 55 # fallback defaults
            if lookup_key in segments:
                start, end, angle, l_short = segments[lookup_key]
                l_long = math.hypot(end[0] - start[0], end[1] - start[1])
                
                # Each slot has a fixed width based on the total capacity
                w = l_long / total_slots
                h = l_short
                
                # Use the berth's number to find its slot, fallback to enumerate index if not numeric
                m = re.search(r'(\d+)', berth.number)
                slot_idx = int(m.group(1)) - 1 if m else idx
                
                fraction = (slot_idx + 0.5) / total_slots
                x = start[0] + fraction * (end[0] - start[0])
                y = start[1] + fraction * (end[1] - start[1])
                rot = angle
                
                # Proportional boat scaling based on length
                if booking and booking.boat and berth.max_length > 0:
                    # We map the berth's visual height (h) to its maximum allowed boat length
                    # Added a 10% margin for visual padding
                    pixels_per_meter = h / (berth.max_length * 1.1)
                    target_pixel_height = booking.boat.length * pixels_per_meter
                    # The SVG boat icon height is 51 units (from y=2 to y=53)
                    boat_scale = target_pixel_height / 51.0
                else:
                    # Fallback to standard fitting
                    boat_scale = min(w / 14.0, h / 40.0) * 0.85 if w > 0 else 1
                
                # Cap the scale to avoid UI glitches with extreme data
                boat_scale = max(min(boat_scale, 2.0), 0.2)
                
                # Rotation adjustment: Stern to sea.
                # B, D and E need 0 while A and C need 180 for correct orientation.
                boat_rot_base = 180
                if berth.block.name in ['B', 'D', 'E']:
                    boat_rot_base = 0
                
                all_berths.append({
                    'obj': berth,
                    'booking': booking,
                    'x': x,
                    'y': y,
                    'rot': rot,
                    'w': w,
                    'h': h,
                    'half_w': w / 2.0,
                    'half_h': h / 2.0,
                    'boat_scale': boat_scale,
                    'boat_rotation': boat_rot_base,
                    'font_size': 5.0 * boat_scale,
                    'empty_font_size': 7.0 * boat_scale,
                    'half_empty_font_size': (7.0 * boat_scale) / 2.0,
                    'boat_name': booking.boat.name if booking else '',
                    'boat_color': booking.boat.color if booking and booking.boat.color else berth.block.color,
                    'owner': booking.boat.owner.name if booking else '',
                    'length': booking.boat.length if booking else '',
                    'start': booking.start_date.strftime('%d.%m.%Y') if booking else '',
                    'end': booking.end_date.strftime('%d.%m.%Y') if booking else '',
                    'flag': booking.boat.flag if booking else '',
                })
    
    # Extra Dashboard Data for Quick Actions and Overview
    upcoming_arrivals = Booking.objects.filter(
        start_date__gte=today
    ).exclude(
        status__in=['COMPLETED', 'CANCELLED']
    ).select_related('boat', 'boat__owner').order_by('start_date')[:5]
    
    upcoming_departures = Booking.objects.filter(
        end_date__gte=today,
        status='ACTIVE'
    ).select_related('boat', 'boat__owner').order_by('end_date')[:5]
    
    pending_invoices = Invoice.objects.filter(status='OPEN').order_by('-date')[:5]
    unpaid_count = Invoice.objects.filter(status='OPEN').count()
    unpaid_total = Invoice.objects.filter(status='OPEN').aggregate(total=models.Sum('total_amount'))['total'] or 0

    context = {
        'berths_count': berths_count,
        'active_bookings': active_bookings,
        'customers_count': customers_count,
        'block_labels': block_labels,
        'block_colors': block_colors,
        'block_occupancy': block_occupancy,
        'block_stats': block_stats,
        'all_berths': all_berths,
        'upcoming_arrivals': upcoming_arrivals,
        'upcoming_departures': upcoming_departures,
        'pending_invoices': pending_invoices,
        'unpaid_count': unpaid_count,
        'unpaid_total': unpaid_total,
        'total_percent': total_percent,
        'today': today,
    }
    return render(request, 'marina/dashboard.html', context)

@login_required
def calendar_view(request):
    return render(request, 'marina/calendar.html')

@login_required
def berths_grid(request):
    from django.utils import timezone
    today = timezone.now().date()
    blocks = Block.objects.all().order_by('name').prefetch_related('berths')
    
    # Pre-calculate status for each berth to avoid N+1 queries in template
    for block in blocks:
        block.berth_list = []
        for berth in block.berths.all().order_by(Length('number').asc(), 'number'):
            current_booking = Booking.objects.filter(
                berth=berth, 
                start_date__lte=today, 
                end_date__gte=today,
                status='ACTIVE'
            ).select_related('boat', 'boat__owner').first()
            
            status = 'Vacant'
            if current_booking:
                if current_booking.is_at_sea:
                    status = 'At Sea (Sub-lease Available)'
                else:
                    status = 'Occupied'
            
            berth.current_status = status
            berth.current_booking = current_booking
            block.berth_list.append(berth)
            
    return render(request, 'marina/berths_grid.html', {'blocks': blocks})

@login_required
def invoices_list(request):
    from django.utils import timezone
    invoices = Invoice.objects.all().prefetch_related('items', 'customer').order_by('-date')
    return render(request, 'marina/invoices_list.html', {
        'invoices': invoices,
        'today': timezone.now().date()
    })

@login_required
def bookings_list(request):
    bookings = Booking.objects.all().select_related('boat', 'boat__owner', 'berth', 'berth__block').order_by('-start_date')
    return render(request, 'marina/bookings_list.html', {'bookings': bookings})

def invoice_mark_paid(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    invoice.status = 'PAID'
    invoice.save()
    return redirect('invoices_list')

def invoice_create(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save()
            return redirect('invoice_edit', pk=invoice.pk)
        else:
            print(f"DEBUG: InvoiceForm invalid: {form.errors}")
    else:
        form = InvoiceForm()
    
    template = 'marina/partials/invoice_create_modal.html'
    if not request.htmx:
        template = 'marina/full_page_modal.html'
        
    return render(request, template, {
        'form': form,
        'partial_template': 'marina/partials/invoice_create_modal.html',
        'title': 'Create New Invoice'
    })

def invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        invoice.delete()
        return redirect('invoices_list')
    return render(request, 'marina/partials/invoice_delete_confirm.html', {'invoice': invoice})

def invoice_edit(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            form.save()
            invoice.recalculate_total()
            if request.htmx:
                response = HttpResponse()
                response['HX-Refresh'] = 'true'
                return response
            return redirect('invoices_list')
    else:
        form = InvoiceForm(instance=invoice)
    
    # These should be available for both GET and invalid POST
    item_form = InvoiceItemForm()
    services = Service.objects.all().order_by('name')
    
    template = 'marina/partials/invoice_edit_modal.html'
    if not request.htmx:
        template = 'marina/full_page_modal.html'
        
    return render(request, template, {
        'invoice': invoice,
        'form': form,
        'item_form': item_form,
        'services': services,
        'partial_template': 'marina/partials/invoice_edit_modal.html',
        'title': f'Edit Invoice #{invoice.id}',
        'wrapper_class': 'col-lg-10 col-xl-9 col-xxl-8 col-md-12'
    })

@login_required
def invoice_add_item(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        # Also save header if present in request
        header_form = InvoiceForm(request.POST, instance=invoice)
        if header_form.is_valid():
            header_form.save()

        form = InvoiceItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.invoice = invoice
            item.save()
            invoice.recalculate_total()
            
    if request.htmx:
        # Re-render the whole modal to keep state consistent
        form = InvoiceForm(instance=invoice)
        item_form = InvoiceItemForm()
        services = Service.objects.all().order_by('name')
        return render(request, 'marina/partials/invoice_edit_modal.html', {
            'invoice': invoice,
            'form': form,
            'item_form': item_form,
            'services': services,
            'title': f'Edit Invoice #{invoice.id}'
        })
    return redirect('invoice_edit', pk=pk)

@login_required
def invoice_remove_item(request, pk):
    item = get_object_or_404(InvoiceItem, pk=pk)
    invoice = item.invoice
    
    if request.method == 'POST':
        # Also save header if present in request
        header_form = InvoiceForm(request.POST, instance=invoice)
        if header_form.is_valid():
            header_form.save()
            
    item.delete()
    invoice.recalculate_total()
    
    if request.htmx:
        form = InvoiceForm(instance=invoice)
        item_form = InvoiceItemForm()
        services = Service.objects.all().order_by('name')
        return render(request, 'marina/partials/invoice_edit_modal.html', {
            'invoice': invoice,
            'form': form,
            'item_form': item_form,
            'services': services,
            'title': f'Edit Invoice #{invoice.id}'
        })
    return redirect('invoice_edit', pk=invoice.id)

@login_required
def customers_list(request):
    # Helper to map flags
    def get_flag_code(code):
        if not code: return 'un'
        mapping = {'UK': 'GB', 'EL': 'GR', 'US': 'US'}
        return mapping.get(code.upper(), code.lower())

    customers = Customer.objects.all().prefetch_related('boats').order_by('name')
    data = []
    for c in customers:
        boats_data = []
        for b in c.boats.all():
            boats_data.append({
                'id': b.id,
                'name': b.name,
                'boat_type': b.get_boat_type_display(),
                'flag': b.flag,
                'flag_code': get_flag_code(b.flag),
                'length': str(b.length),
                'width': str(b.width),
                'draft': str(b.draft),
                'weight': str(b.weight),
                'diesel': str(b.diesel_tank),
                'water': str(b.water_tank),
                'image_url': b.image.url if b.image else '/static/img/no-boat.png',
                'notes': b.notes
            })
        
        data.append({
            'id': c.id,
            'name': c.name,
            'email': c.email,
            'phone': c.phone,
            'address': c.address,
            'boats': boats_data,
            'boat_count': len(boats_data)
        })
    
    import json
    customers_json = json.dumps(data)
    
    return render(request, 'marina/customers_list.html', {
        'customers_json': customers_json
    })

@login_required
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            if request.htmx:
                return HttpResponse('<script>window.location.reload();</script>')
            return redirect('customers_list')
    else:
        form = CustomerForm()
    
    return render(request, 'marina/partials/customer_form_modal.html', {
        'form': form,
        'editing': False
    })

@login_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            if request.htmx:
                return HttpResponse('<script>window.location.reload();</script>')
            return redirect('customers_list')
    else:
        form = CustomerForm(instance=customer)
    
    return render(request, 'marina/partials/customer_form_modal.html', {
        'form': form,
        'customer': customer,
        'editing': True
    })

@login_required
def providers_list(request):
    providers = ServiceProvider.objects.all().order_by('name')
    return render(request, 'marina/providers_list.html', {'providers': providers})

def provider_create(request):
    from .forms import ServiceProviderForm
    if request.method == 'POST':
        form = ServiceProviderForm(request.POST)
        if form.is_valid():
            form.save()
            if request.htmx:
                response = HttpResponse()
                response['HX-Refresh'] = 'true'
                return response
            return redirect('providers_list')
    else:
        form = ServiceProviderForm()
    
    template = 'marina/partials/provider_form.html'
    if not request.htmx:
        template = 'marina/full_page_modal.html'
    
    return render(request, template, {
        'form': form,
        'partial_template': 'marina/partials/provider_form.html',
        'title': 'New Service Provider'
    })

def provider_edit(request, pk):
    from .forms import ServiceProviderForm
    provider = get_object_or_404(ServiceProvider, pk=pk)
    if request.method == 'POST':
        form = ServiceProviderForm(request.POST, instance=provider)
        if form.is_valid():
            form.save()
            if request.htmx:
                response = HttpResponse()
                response['HX-Refresh'] = 'true'
                return response
            return redirect('providers_list')
    else:
        form = ServiceProviderForm(instance=provider)
    
    template = 'marina/partials/provider_form.html'
    if not request.htmx:
        template = 'marina/full_page_modal.html'
    
    return render(request, template, {
        'form': form,
        'partial_template': 'marina/partials/provider_form.html',
        'title': f'Edit Provider: {provider.name}'
    })

def provider_delete(request, pk):
    provider = get_object_or_404(ServiceProvider, pk=pk)
    if request.method == 'POST':
        provider.delete()
        return redirect('providers_list')
    return render(request, 'marina/partials/provider_delete_confirm.html', {'provider': provider})

@login_required
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

@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        return redirect('customers_list')
    return render(request, 'marina/partials/customer_delete_confirm.html', {'customer': customer})

@login_required
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

@login_required
def boat_delete(request, pk):
    boat = get_object_or_404(Boat, pk=pk)
    if request.method == 'POST':
        boat.delete()
        return redirect('customers_list')
    return render(request, 'marina/partials/boat_delete_confirm.html', {'boat': boat})

@login_required
def planning_grid(request):
    return render(request, 'marina/planning_grid.html')

@login_required
def reports_view(request):
    from django.db.models import Sum, Count, Avg
    from django.db.models.functions import TruncMonth
    from django.utils import timezone
    from datetime import timedelta
    
    today = timezone.now().date()
    first_of_month = today.replace(day=1)
    
    # 1. Revenue Analytics
    revenue_data = Invoice.objects.filter(status='PAID').annotate(
        month=TruncMonth('date')
    ).values('month').annotate(total=Sum('total_amount')).order_by('month')
    
    this_month_revenue = Invoice.objects.filter(
        status='PAID', 
        date__gte=first_of_month
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # 2. Occupancy & Capacity
    berths_total = Berth.objects.count()
    active_bookings = Booking.objects.filter(status='ACTIVE').count()
    planned_bookings = Booking.objects.filter(status='PLANNED', start_date__gte=today).count()
    occupancy_rate = (active_bookings / berths_total * 100) if berths_total > 0 else 0
    
    # 3. Customer & Boat Analytics
    top_customers = Customer.objects.annotate(
        total_spent=Sum('invoices__total_amount')
    ).order_by('-total_spent')[:5]
    
    boat_types = Boat.objects.values('boat_type').annotate(count=Count('id')).order_by('-count')
    # Map choices
    boat_type_labels = dict(Boat.BOAT_TYPES)
    boat_types_data = [
        {'label': boat_type_labels.get(bt['boat_type'], bt['boat_type']), 'count': bt['count']} 
        for bt in boat_types
    ]
    
    nationalities = Boat.objects.values('flag').annotate(count=Count('id')).order_by('-count')[:8]
    
    # 4. Service Revenue
    service_revenue = InvoiceItem.objects.filter(
        invoice__status='PAID',
        description__icontains='Service:'
    ).values('description').annotate(total=Sum('unit_price')).order_by('-total')[:5]

    context = {
        'revenue_data': [
            {'month': d['month'].strftime('%Y-%m-%d') if d['month'] else None, 'total': float(d['total'])} 
            for d in revenue_data
        ],
        'this_month_revenue': float(this_month_revenue),
        'occupancy_rate': round(occupancy_rate, 1),
        'active_bookings': active_bookings,
        'planned_bookings': planned_bookings,
        'top_customers': top_customers,
        'avg_boat_length': round(Boat.objects.aggregate(Avg('length'))['length__avg'] or 0, 1),
        'boat_types_json': list(boat_types_data),
        'nationalities_json': list(nationalities),
        'service_revenue': [
            {'description': s['description'], 'total': float(s['total'])} 
            for s in service_revenue
        ],
    }
    return render(request, 'marina/reports.html', context)

@login_required
def api_planning_data(request):
    import datetime
    year = int(request.GET.get('year', datetime.date.today().year))
    start_date = datetime.date(year, 1, 1)
    end_date = datetime.date(year, 12, 31)
    from .models import Block, Berth
    blocks = Block.objects.all().order_by('name')
    berths = Berth.objects.all().select_related('block').order_by('block__name', 'number')
    resources = []
    for idx, block in enumerate(blocks):
        berth_ids = [str(b.id) for b in block.berths.all()]
        resources.append({
            'id': f"block_{block.id}",
            'content': f"Block {block.name}",
            'nestedGroups': berth_ids,
            'className': 'bg-light fw-bold',
            'color': block.color,
            'block_type': block.block_type,
            'order': idx * 1000
        })
    for berth in berths:
        resources.append({
            'id': str(berth.id),
            'content': f"{berth.number}",
            'block_color': berth.block.color,
            'block_type': berth.block.block_type,
            'order': int(berth.number) if str(berth.number).isdigit() else 999
        })
    bookings = Booking.objects.filter(start_date__lte=end_date, end_date__gte=start_date).select_related('boat', 'boat__owner', 'berth')
    items = []
    for b in bookings:
        flag = (b.boat.flag or 'xx').lower()
        base_color = b.boat.color or '#3498db'
        style = f"background-color: {base_color}; border-color: {base_color}; color: white;"
        if b.is_at_sea:
            style = f"background-image: linear-gradient(45deg, rgba(0,0,0,0.3) 25%, transparent 25%, transparent 50%, rgba(0,0,0,0.3) 50%, rgba(0,0,0,0.3) 75%, transparent 75%, transparent); background-size: 8px 8px; background-color: {base_color}; border: 1px solid {base_color}; color: white;"
        items.append({
            'id': b.id,
            'group': str(b.berth_id),
            'start': b.start_date.isoformat(),
            'end': (b.end_date + datetime.timedelta(days=1)).isoformat(),
            'content': f"{b.boat.name} (SEA)" if b.is_at_sea else b.boat.name,
            'flag': flag,
            'style': style,
            'owner': b.boat.owner.name if b.boat.owner else '',
            'boat_type': b.boat.get_boat_type_display(),
            'boat_image': b.boat.image.url if b.boat.image else '/static/img/default-boat.png',
            'arrival': b.start_date.strftime('%d.%m.%Y'),
            'departure': b.end_date.strftime('%d.%m.%Y'),
            'phone': b.boat.owner.phone if (b.boat.owner) else '',
            'engine': b.boat.engine,
            'specs': f"{b.boat.length}m x {b.boat.width}m",
            'draft': b.boat.draft,
            'diesel': b.boat.diesel_tank,
            'water': b.boat.water_tank,
            'language': b.boat.owner.language if b.boat.owner else '',
            'year': b.boat.year_built,
            'notes': b.notes,
            'ref': b.reference,
            'category': 'booking'
        })
    scheduled_orders = WorkOrder.objects.filter(start_date__isnull=False, start_date__lte=end_date, end_date__gte=start_date).select_related('boat', 'boat__owner', 'berth')
    service_items = []
    unassigned_exists = False
    for s in scheduled_orders:
        style = f"background-color: #f39c12; border-color: #e67e22; color: white;"
        if s.status == 'COMPLETED': style = f"background-color: #27ae60; border-color: #2ecc71; color: white;"
        elif s.status == 'IN_PROGRESS': style = f"background-color: #3498db; border-color: #2980b9; color: white;"
        
        group_id = 'group_services'
        if s.berth: 
            group_id = str(s.berth_id)
        else:
            active_b = Booking.objects.filter(boat=s.boat, start_date__lte=s.start_date, end_date__gte=s.start_date).first()
            if active_b: 
                group_id = str(active_b.berth_id)
            else:
                unassigned_exists = True

        # Get list of services in this order for content
        item_names = ", ".join([item.service.name for item in s.items.all()])
        content = f"🛠 {item_names if item_names else 'Empty Order'}"

        service_items.append({
            'id': f"service_{s.id}",
            'group': group_id,
            'start': s.start_date.isoformat(),
            'end': (s.end_date + datetime.timedelta(days=1)).isoformat() if s.end_date else (s.start_date + datetime.timedelta(days=1)).isoformat(),
            'content': content,
            'style': style,
            'owner': s.customer.name if s.customer else (s.boat.owner.name if s.boat.owner else ''),
            'boat_type': s.boat.get_boat_type_display(),
            'boat_image': s.boat.image.url if s.boat.image else '/static/img/no-boat.png',
            'arrival': s.start_date.strftime('%d.%m.%Y'),
            'departure': s.end_date.strftime('%d.%m.%Y') if s.end_date else '-',
            'phone': (s.customer.phone if s.customer else (s.boat.owner.phone if s.boat.owner else '')),
            'engine': s.boat.engine or '-',
            'specs': f"{s.boat.length}m x {s.boat.width}m",
            'draft': s.boat.draft,
            'diesel': s.boat.diesel_tank,
            'water': s.boat.water_tank,
            'language': (s.customer.language if s.customer else (s.boat.owner.language if s.boat.owner else '')),
            'year': s.boat.year_built,
            'ref': s.get_status_display(),
            'notes': s.notes or '',
            'category': 'service',
            'order_id': s.id
        })
    
    if unassigned_exists:
        resources.append({'id': 'group_services', 'content': 'Unassigned Services', 'className': 'bg-warning-soft fw-bold', 'order': 9999})
    
    items.extend(service_items)
    return JsonResponse({'groups': resources, 'items': items}, safe=False)

@login_required
def api_resources(request):
    from .models import Block, Berth
    blocks = Block.objects.all().order_by('name')
    berths = Berth.objects.all().select_related('block').order_by('block__name', 'number')
    resources = []
    for idx, block in enumerate(blocks):
        resources.append({
            'id': f"block_{block.id}",
            'content': f"Block {block.name}",
            'nestedGroups': [str(b.id) for b in block.berths.all()],
            'className': 'bg-light fw-bold',
            'block_type': block.block_type,
            'order': idx * 1000
        })
    for berth in berths:
        try: b_order = int(berth.number)
        except ValueError: b_order = 999
        resources.append({
            'id': str(berth.id),
            'content': f"{berth.number}",
            'block_color': berth.block.color,
            'block_type': berth.block.block_type,
            'order': b_order
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
    
    import datetime
    events = []
    for b in bookings:
        events.append({
            'id': b.id,
            'text': f"{b.boat.name}",
            'start': b.start_date.isoformat(),
            'end': (b.end_date + datetime.timedelta(days=1)).isoformat(),
            'resource': b.berth.id,
            'type': b.booking_type,
            'is_at_sea': b.is_at_sea,
            'color': b.boat.color,
            'flag': (b.boat.flag or 'xx').lower(),
            'owner': b.boat.owner.name if b.boat.owner else '',
            'phone': b.boat.owner.phone if b.boat.owner else '',
            'image': b.boat.image.url if b.boat.image else '/static/img/no-boat.png',
            'boat_type': b.boat.get_boat_type_display(),
            'engine': b.boat.engine,
            'length': b.boat.length,
            'width': b.boat.width,
            'draft': b.boat.draft,
            'diesel': b.boat.diesel_tank if hasattr(b.boat, 'diesel_tank') else 0,
            'water': b.boat.water_tank if hasattr(b.boat, 'water_tank') else 0,
            'language': b.boat.owner.language if b.boat.owner else '',
            'year': b.boat.year_built if hasattr(b.boat, 'year_built') else '',
            'ref': b.reference,
            'notes': b.notes
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
            'current_boat': current_booking.boat.name if (current_booking and current_booking.boat) else 'None',
            'owner': current_booking.boat.owner.name if (current_booking and current_booking.boat and current_booking.boat.owner) else 'None',
            'owner_email': current_booking.boat.owner.email if (current_booking and current_booking.boat and current_booking.boat.owner) else '',
            'phone': current_booking.boat.owner.phone if (current_booking and current_booking.boat and current_booking.boat.owner) else '',
            'flag': (current_booking.boat.flag or 'xx').lower() if (current_booking and current_booking.boat) else '',
            'engine': current_booking.boat.engine if (current_booking and current_booking.boat) else '',
            'length': current_booking.boat.length if (current_booking and current_booking.boat) else '',
            'width': current_booking.boat.width if (current_booking and current_booking.boat) else 0,
            'draft': current_booking.boat.draft if (current_booking and current_booking.boat) else 0,
            'diesel': current_booking.boat.diesel_tank if (current_booking and current_booking.boat) else 0,
            'water': current_booking.boat.water_tank if (current_booking and current_booking.boat) else 0,
            'year': current_booking.boat.year_built if (current_booking and current_booking.boat) else '',
            'language': current_booking.boat.owner.language if (current_booking and current_booking.boat and current_booking.boat.owner) else '',
            'notes': current_booking.notes if current_booking else '',
            'ref': current_booking.reference if current_booking else '',
            'check_in': current_booking.start_date.strftime('%d.%m.%Y') if current_booking else '',
            'check_out': current_booking.end_date.strftime('%d.%m.%Y') if current_booking else '',
            'boat_type': current_booking.boat.boat_type if (current_booking and current_booking.boat) else '',
            'boat_image': current_booking.boat.image.url if (current_booking and current_booking.boat and current_booking.boat.image) else '/static/img/default-boat.png',
            'boat_id': current_booking.boat.id if (current_booking and current_booking.boat) else None,
            'booking_id': current_booking.id if current_booking else None,
            'status': status
        })
    return JsonResponse(data, safe=False)

@login_required
def api_bookings(request):
    # Fetch normal bookings
    bookings = Booking.objects.all().select_related('boat', 'boat__owner', 'berth', 'berth__block').prefetch_related('supplies__service')
    
    # Fetch work orders that occupy a berth
    work_orders = WorkOrder.objects.filter(berth__isnull=False).select_related('boat', 'boat__owner', 'berth', 'berth__block').prefetch_related('items__service')
    
    data = []
    
    # Normal Bookings (Marina)
    for b in bookings:
        supplies = []
        for supply in b.supplies.all():
            supplies.append({
                'name': supply.service.name,
                'quantity': supply.quantity,
                'total': float(supply.total_price)
            })
            
        data.append({
            'id': f"b-{b.id}",
            'real_id': b.id,
            'type_group': 'marina',
            'boat_name': b.boat.name,
            'boat_id': b.boat.id,
            'owner_name': b.boat.owner.name,
            'flag': b.boat.get_flag_code(),
            'berth_num': b.berth.number,
            'berth_id': b.berth.id,
            'block_name': b.berth.block.name,
            'block_color': b.berth.block.color,
            'start_date': b.start_date.strftime('%d.%m.%Y'),
            'end_date': b.end_date.strftime('%d.%m.%Y'),
            'start_iso': b.start_date.isoformat(),
            'end_iso': b.end_date.isoformat(),
            'status': b.get_status_display(),
            'status_code': b.status,
            'type': 'Booking',
            'services': supplies,
            'total_services': sum(s['total'] for s in supplies),
            'notes': b.notes,
            'color': '#3498db' # Blue for Marina
        })
        
    # Work Orders (Yard)
    for w in work_orders:
        if not w.start_date or not w.end_date:
            continue
            
        items = []
        for item in w.items.all():
            items.append({
                'name': item.service.name,
                'quantity': item.quantity,
                'total': float(item.total_price)
            })
            
        data.append({
            'id': f"w-{w.id}",
            'real_id': w.id,
            'type_group': 'yard',
            'boat_name': w.boat.name,
            'boat_id': w.boat.id,
            'owner_name': w.customer.name if w.customer else w.boat.owner.name,
            'flag': w.boat.get_flag_code(),
            'berth_num': w.berth.number,
            'berth_id': w.berth.id,
            'block_name': w.berth.block.name,
            'block_color': w.berth.block.color,
            'start_date': w.start_date.strftime('%d.%m.%Y'),
            'end_date': w.end_date.strftime('%d.%m.%Y'),
            'start_iso': w.start_date.isoformat(),
            'end_iso': w.end_date.isoformat(),
            'status': w.get_status_display(),
            'status_code': w.status,
            'type': 'Repair/Yard',
            'services': items,
            'total_services': sum(s['total'] for s in items),
            'notes': w.notes,
            'color': '#f39c12' # Orange for Yard
        })
        
    return JsonResponse(data, safe=False)
@login_required
def invoice_submit_mydata(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    success, message = send_invoice_to_mydata(invoice)
    if success:
        messages.success(request, f'Invoice #{invoice.id} submitted to myDATA! {message}')
    else:
        messages.error(request, f'myDATA Submission Failed: {message}')
    return redirect('invoices_list')
