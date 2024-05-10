from django.urls import path
from . import views

urlpatterns = [
  path('',  views.hello, name= "hello"),
  path('check/', views.check, name='check'),
  path('eliminar_producto_venta/<int:producto_venta_id>/', views.eliminar_producto_venta, name='eliminar_producto_venta'),
  path('finalizar_venta/', views.finalizar_venta, name='finalizar_venta'),

 ]
