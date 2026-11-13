from django.urls import path
from . import views

urlpatterns = [
    path('', views.mostrar_home, name='home'), # La raíz (ej: http://127.0.0.1:8000/) abre el login
    
    # path('home/', views.home_view, name='home'),
    
    # Rutas para la gestión de pacientes
    path('pacientes/', views.gestion_pacientes_view, name='gestion_pacientes'),
    path('pacientes/crear/', views.crear_paciente_view, name='crear_paciente'),
    path('pacientes/<int:paciente_id>/editar/', views.editar_paciente_view, name='editar_paciente'),
    
    path('pacientes/<int:paciente_id>/recetas/crear/', views.crear_receta_view, name='crear_receta'),
    
    # Rutas para la gestión de enfermeros
    path('enfermeros/', views.mostrar_enfermeros, name='gestion_enfermeros'),
    path('enfermero/<int:enfermero_id>/aprobar/', views.aprobar_enfermero_view, name='aprobar_enfermero' ),
    path('enfermero/<int:enfermero_id>/baja/', views.dar_baja_enfermero_view, name='dar_baja_enfermero' ),
    
    # Rutas para la gestión de camas
    path('camas/', views.mostrar_sector_camas, name='sector_camas'),
    path('cama/<int:cama_id>/liberar/', views.liberar_cama_view, name='liberar_cama'),
    path('cama/<int:cama_id>/asignar/', views.asignar_paciente_view, name='asignar_paciente'),

    # Rutas para el login, logout y registro de usuarios
    path('login/', views.mostrar_login_usuario, name='login_usuario'),
    path('logout/', views.cerrar_sesion, name='cerrar_sesion'),
    path('registro/', views.mostrar_registro_usuario, name='registro_usuario'),
    
    #Rutas planillas
    path('planillas/', views.mostrar_planillas, name='gestion_planillas'),
    path('planillas/<int:paciente_id>/', views.mostrar_planillas, name='gestion_planillas'),
    path('planillas/paciente/<int:paciente_id>/guardar/', views.guardar_administracion, name='guardar_administracion'),
    path('planillas/registro/<int:registro_id>/eliminar/', views.eliminar_administracion, name='eliminar_administracion'),
    
]