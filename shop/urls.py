from django.urls import path
from . import views

 
urlpatterns =[
    path('' , views.shop_view,name='shop'),
    path('product_detail/' , views.product_detail,name='product_detail'),
    path('cart/' , views.cart,name='cart'),
    path('checkout/' , views.checkout,name='checkout'),
    # path('categories/<int:id>/', views.category_view, name='category-view'),
    # path('<int:id>/', views.prod_view, name='product'),
    #  # ADD TO CART
    # path('add_to_cart/<int:project_id>/', views.add_to_cart, name='add_to_cart'),
    # # DECREASE CART
    # path('decrease_cart/<int:project_id>/', views.decrease_cart, name='decrease_cart'),
    # # DELETE CART ITEM
    # path('delete_cart/<int:cart_id>/', views.delete_cart, name='delete_cart'),
    # path('cart/', views.cart_view,name='cart'),
    
    # path('checkout/', views.checkout_view,name='checkout')
   
]