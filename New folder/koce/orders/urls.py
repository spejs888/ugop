from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('order/new/', views.create_order, name='create_order'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/<int:order_id>/add_item/', views.add_item, name='add_item'),
    path('order/<int:order_id>/remove_item/<int:item_id>/', views.remove_item, name='remove_item'),
    path('order/<int:order_id>/print_fiscal/', views.print_fiscal, name='print_fiscal'),
    path('order/<int:order_id>/print_cash/', views.print_cash, name='print_cash'),
    path('table/<int:table_number>/', views.table_view, name='table_view'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('kitchen/pici/', views.pici_queue, name='pici_queue'),
    path('kitchen/kitchen/', views.kitchen_queue, name='kitchen_queue'),
    path('kitchen/bar/', views.bar_queue, name='bar_queue'),
    path('kitchen/realtime/', views.kitchen_realtime, name='kitchen_realtime'),
    path('api/pici/', views.api_pici, name='api_pici'),
    path('api/kitchen/', views.api_kitchen, name='api_kitchen'),
    path('api/bar/', views.api_bar, name='api_bar'),
    path('reports/', views.manager_report, name='manager_report'),
]
