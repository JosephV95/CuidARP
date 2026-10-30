from django.shortcuts import render, redirect
from django.contrib import messages  # Para mostrar alertas amigables
from django.contrib.auth import authenticate, login, logout

#Importar los modelos de la app funcionalidades
from .models import Enfermero

# Create your views here.
def mostrar_registro_usuario(request):
    if request.method == 'POST':
        # 1 Capturamos los datos enviados desde el formulario HTML
        nombre_form = request.POST.get('nombre',' ')  # Valor por defecto vacío si no se encuentra
        apellido_form = request.POST.get('apellido',' ') # Valor por defecto vacío si no se encuentra
        dni_form = request.POST.get('dni',' ') # Valor por defecto vacío si no se encuentra
        matricula_form = request.POST.get('matricula',' ') 
        telefono_form = request.POST.get('telefono',' ') 
        email_form = request.POST.get('email',' ') 
        tipo_prof_form = request.POST.get('tipo_profesional',' ') 
        servicio_form = request.POST.get('servicio',' ') 
        rol_form = request.POST.get('rol',' ') 
        pin_form = request.POST.get('pin_sello',' ') 
        password_form = request.POST.get('password',' ')  # Nota: A futuro lo ideal es encriptarla

        # 2 Validamos de forma unificada si ya existe DNI, Email o Matrícula
        error_encontrado = False
        
        # Validar si ya existe un enfermero con el mismo DNI o Email
        if Enfermero.objects.filter(dni=dni_form).exists():
            messages.error(
                request,
                'El DNI ingresado ya se encuentra registrado en el sistema.',
            )
            error_encontrado = True

        if Enfermero.objects.filter(email=email_form).exists():
            messages.error(
                request,
                'El correo electrónico ingresado ya está en uso por otro profesional.',
            )
            error_encontrado = True

        if Enfermero.objects.filter(matricula=matricula_form).exists():
            messages.error(
                request, 'El número de matrícula ingresado ya está registrado.'
            )
            error_encontrado = True

        # 3. Si hubo CUALQUIER error, devolvemos el template UNA SOLA VEZ con los datos
        if error_encontrado:
            return render(
                request,
                'Registro_Usuario.html',
                {
                    'nombre': nombre_form,
                    'apellido': apellido_form,
                    'dni': dni_form,
                    'matricula': matricula_form,
                    'telefono': telefono_form,
                    'email': email_form,
                    'tipo_profesional': tipo_prof_form,
                    'servicio': servicio_form,
                    'rol': rol_form,
                    'pin_sello': pin_form,
                    'password': password_form,  # La contraseña por seguridad suele limpiarse, pero puedes pasarla si deseas
                },
            )
        
        # 4 Si pasa las validaciones, creamos el usuario (verificado=False por defecto)
        # Creamos la instancia del objeto en memoria (aún no se guarda)
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
            verificado=False,  # Pendiente de aprobación
        )
        
        nuevo_enfermero.save()  # * Guardamos el objeto en la base de datos
        # login(request, nuevo_enfermero)  # Iniciamos sesión automáticamente para el usuario recién registrado
        
        # Mensaje de éxito informando que su cuenta requiere aprobación
        messages.success(
            request,
            '¡Registro exitoso! Su cuenta ha sido creada pero se encuentra'
            ' pendiente de aprobación por un superior.',
        )
        # Redirigimos al LOGIN como bien sugeriste, no al home
        return redirect('login_usuario')  
    
    else:  # Si la petición es GET, simplemente mostramos el formulario vacío
        return render(request, 'Registro_Usuario.html')



# ? Autenticacion del usuario (login) 
def mostrar_login_usuario(request):
    if request.method == 'POST':
        username_form = request.POST.get('username')
        password_form = request.POST.get('password')
        
        user_exists = Enfermero.objects.filter(email=username_form, password=password_form).exists()
        
        if user_exists:
            # Si el usuario existe, redirigimos a la página principal o dashboard
            return redirect('home')
        else:
            # Si el usuario no existe, podemos mostrar un mensaje de error o redirigir al login nuevamente
            return render(request, 'Login_Usuario.html', {'error': 'Credenciales inválidas. Por favor, inténtelo de nuevo.'})
        
        
    
    else:
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

