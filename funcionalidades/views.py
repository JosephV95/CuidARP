from django.shortcuts import render, redirect

#Importar los modelos de la app funcionalidades
from .models import Enfermero

# Create your views here.
def mostrar_registro_usuario(request):
    if request.method == 'POST':
        # 1. Capturamos los datos enviados desde el formulario HTML
        nombre_form = request.POST.get('nombre')
        apellido_form = request.POST.get('apellido')
        dni_form = request.POST.get('dni')
        matricula_form = request.POST.get('matricula')
        telefono_form = request.POST.get('telefono')
        email_form = request.POST.get('email')
        tipo_prof_form = request.POST.get('tipo_profesional')
        servicio_form = request.POST.get('servicio')
        rol_form = request.POST.get('rol')
        pin_form = request.POST.get('pin_sello')    
        password_form = request.POST.get('password')  # Nota: A futuro lo ideal es encriptarla

        # 2. Creamos la instancia del objeto en memoria (aún no se guarda)
        nuevo_enfermero = Enfermero(
            nombre=nombre_form,
            apellido=apellido_form,
            dni=dni_form,
            matricula=matricula_form,
            telefono=telefono_form,
            email=email_form,
            tipo_profesional=tipo_prof_form,
            servicio=servicio_form,
            rol=rol_form,
            pin_sello=pin_form,
            password=password_form,  # Guardado directo (ideal hashear en producción)
        )
        
        nuevo_enfermero.save()  # * Guardamos el objeto en la base de datos

        # 3. Redirigimos al usuario al login (o a la página principal) tras registrarse con éxito
        return redirect('home')
    
    else:  # Si la petición es GET, simplemente mostramos el formulario vacío
        return render(request, 'Registro_Usuario.html')


def mostrar_login_usuario(request):
    return render(request, 'Login_Usuario.html')


def mostrar_home(request):
    return render(request, 'Home.html')

def mostrar_pacientes(request):
    return render(request, 'Gestion_Pacientes.html')

def mostrar_enfermeros(request):
    return render(request, 'Gestion_Enfermeros.html')

def mostrar_camas(request):
    return render(request, 'Sector_Camas.html')

def mostrar_planillas(request):
    return render(request, 'Planillas.html')

