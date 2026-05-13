from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from marina import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('berths/', views.berths_grid, name='berths_grid'),
    path('bookings/', views.bookings_list, name='bookings_list'),
    path('invoices/', views.invoices_list, name='invoices_list'),
    path('customers/', views.customers_list, name='customers_list'),
    path('customers/edit/<int:pk>/', views.customer_edit, name='customer_edit'),
    path('customers/delete/<int:pk>/', views.customer_delete, name='customer_delete'),
    path('boats/edit/<int:pk>/', views.boat_edit, name='boat_edit'),
    path('boats/delete/<int:pk>/', views.boat_delete, name='boat_delete'),
    path('planning/', views.planning_grid, name='planning_grid'),
    path('booking/create/', views.booking_create, name='booking_create'),
    path('booking/quick-boat/', views.quick_boat_create, name='quick_boat_create'),
    path('booking/edit/<int:booking_id>/', views.booking_edit, name='booking_edit'),
    path('booking/delete/<int:booking_id>/', views.booking_delete, name='booking_delete'),
    path('booking/add-service/<int:booking_id>/', views.add_service, name='add_service'),
    path('checkout/<int:berth_id>/', views.checkout_view, name='checkout'),
    path('reports/', views.reports_view, name='reports'),
    path('api/resources/', views.api_resources, name='api_resources'),
    path('api/events/', views.api_events, name='api_events'),
    path('api/planning-data/', views.api_planning_data, name='api_planning_data'),
    path('api/berths/', views.api_berths, name='api_berths'),
    path('api/bookings/', views.api_bookings, name='api_bookings'),
    path('invoice/create/', views.invoice_create, name='invoice_create'),
    path('invoice/pdf/<int:invoice_id>/', views.invoice_pdf, name='invoice_pdf'),
    path('invoice/edit/<int:pk>/', views.invoice_edit, name='invoice_edit'),
    path('invoice/add-item/<int:pk>/', views.invoice_add_item, name='invoice_add_item'),
    path('invoice/remove-item/<int:pk>/', views.invoice_remove_item, name='invoice_remove_item'),
    path('invoice/mark-paid/<int:pk>/', views.invoice_mark_paid, name='invoice_mark_paid'),
    path('invoice/delete/<int:pk>/', views.invoice_delete, name='invoice_delete'),
    
    # Auth
    path('accounts/', include('django.contrib.auth.urls')),
    
    # PWA
    path('sw.js', TemplateView.as_view(template_name="sw.js", content_type='application/javascript'), name='sw.js'),
    path('offline/', TemplateView.as_view(template_name="marina/offline.html"), name='offline'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
