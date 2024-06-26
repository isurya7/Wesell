from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='admin_dashboard'),
    path('add-product/', views.add_product, name='admin_add_product'),
    path('manage-orders/', views.manage_orders, name='admin_manage_orders'),
    path('view-payment/',views.view_payments,name='view_payment'),
    path('product-in-market/', views.product_in_market, name='admin_product_in_market'),
    path('delete-product/<int:product_id>/', views.delete_product, name='admin_delete_product'),
    path('delete-order/<int:order_id>/', views.delete_order, name='admin_delete_order'),
]