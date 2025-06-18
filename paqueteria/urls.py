from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('menu/', views.menu_principal, name='menu'),
    path('envio/', views.registrar_envio, name='registrar_envio'),
    path('devolucion/', views.registrar_devolucion, name='registrar_devolucion'),
    #path('devolucion/', views.registrar_devolucion, name='registrar_devolucion'),

]
