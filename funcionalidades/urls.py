from django.urls import path
from . import views

urlpatterns = [
    path('', views.mostrar_home, name='home'), # La raíz (ej: http://127.0.0.1:8000/) abre el login
    
    # path('home/', views.home_view, name='home'),
    path('pacientes/', views.mostrar_pacientes, name='gestion_pacientes'),
    path('enfermeros/', views.mostrar_enfermeros, name='gestion_enfermeros'),
    path('camas/', views.mostrar_camas, name='sector_camas'),
    path('planillas/', views.mostrar_planillas, name='gestion_planillas'),
    
    path('login/', views.mostrar_login_usuario, name='login_usuario'),
    path('logout/', views.cerrar_sesion, name='cerrar_sesion'),
    path('registro/', views.mostrar_registro_usuario, name='registro_usuario'),
]