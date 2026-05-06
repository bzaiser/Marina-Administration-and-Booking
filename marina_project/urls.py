from django.contrib import admin
from django.urls import path
from marina import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('berths/', views.berths_grid, name='berths_grid'),
    path('invoices/', views.invoices_list, name='invoices_list'),
    path('customers/', views.customers_list, name='customers_list'),
    path('planning/', views.planning_grid, name='planning_grid'),
    path('booking/create/', views.booking_create, name='booking_create'),
    path('checkout/<int:berth_id>/', views.checkout_view, name='checkout'),
    path('reports/', views.reports_view, name='reports'),
    path('api/resources/', views.api_resources, name='api_resources'),
    path('api/events/', views.api_events, name='api_events'),
    path('api/planning-data/', views.api_planning_data, name='api_planning_data'),
    path('api/berths/', views.api_berths, name='api_berths'),
    path('invoice/pdf/<int:invoice_id>/', views.invoice_pdf, name='invoice_pdf'),
]
