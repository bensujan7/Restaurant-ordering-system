# orders/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('categories/', views.category_list, name='category_list'),
    path('category/add/', views.category_add, name='add_category'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('category/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
    path('dashboard/', views.dashboard, name='dashboard'),
    path('menu/', views.menu_list, name='menu_list'),
    path('menu/add/', views.menu_item_create, name='menu_item_create'),
    path('menu/<int:pk>/edit/', views.menu_item_update, name='menu_item_update'),
    path('menu/<int:pk>/delete/', views.menu_delete_view, name='menu_delete'),

    path('tables/', views.table_list, name='table_list'),
    path('tables/<int:pk>/edit/', views.table_management, name='table_edit'),
    path('tables/<int:pk>/delete/', views.table_delete, name='table_delete'),

    path('pos/', views.order_create, name='order_create'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/history/', views.order_history, name='order_history'),

    path('kitchen/', views.kitchen_display, name='kitchen_display'),
    path('orders/<int:pk>/status/<str:new_status>/', views.update_order_status, name='update_order_status'),
   
]