from django.urls import path, include
from . import views
from account import views as AccountViews

urlpatterns = [
    path('', AccountViews.vendorDashboard, name='vendor'),
    path('profile/', views.vprofile, name='vprofile'),
    path('add_product/', views.add_product, name='add_product'),
    # path('menu-builder/product/edit/<int:pk>/', views.edit_product, name='edit_product'),
    # path('menu-builder/product/delete/<int:pk>/', views.delete_product, name='delete_product'),

    # path('order_detail/<int:order_number>/', views.order_detail, name='vendor_order_detail'),
    # path('vendor_order_detail/<int:order_number>/', views.order_detail, name='vendor_order_detail'),
    # path('my_orders/', views.my_orders, name='vendor_my_orders'),
    # path('active_farms/', views.active_farms, name='active farms'),
    # path('completed_farms/', views.completed_farms, name='completed_farms'),
    # path('vendor/active_farms/<int:project_id>/save_status/', views.save_status, name='save_status'),
    # path('farm_status/<int:id>/', views.farm_status, name='farm_status'),
]