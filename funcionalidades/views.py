from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages  # Para mostrar alertas amigables
from django.contrib.auth import authenticate, login, logout
import json  # Para convertir datos de Python a JSON y enviarlos al template

#Importar los modelos de la app funcionalidades
from .models import Enfermero, Paciente, Sector, Habitacion, Cama

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



#? Autenticacion del usuario (login) 
def mostrar_login_usuario(request):
    if request.method == 'POST':
        identificador = request.POST.get( 'username' )  # Puede ser DNI o Correo Electrónico
        password_ingresada = request.POST.get('password')

        # Buscamos al enfermero por DNI o por Email
        enfermero = Enfermero.objects.filter(dni=identificador).first() or Enfermero.objects.filter(email=identificador).first()

        if enfermero:
             # Verificamos la contraseña
            if enfermero.password == password_ingresada:

                # 1. VALIDACIÓN CLAVE: ¿Está verificado por el Jefe de Enfermeros?
                if not enfermero.verificado:
                    messages.warning(
                        request,
                        'Su cuenta se encuentra pendiente de aprobación por un Jefe de'
                        ' Enfermeros.',
                    )
                    return render(request, 'Login_Usuario.html')

                # 2. CREAMOS LA SESIÓN: Guardamos los datos clave en la sesión del navegador
                request.session['enfermero_id'] = enfermero.id
                request.session['nombre'] = enfermero.nombre
                request.session['apellido'] = enfermero.apellido
                request.session['nombre_completo'] = (
                    f'{enfermero.nombre} {enfermero.apellido}'
                )
                request.session['rol'] = enfermero.rol
                request.session['servicio'] = enfermero.servicio

                messages.success(request, f'¡Bienvenido/a, {enfermero.nombre}!')

                # 3. Redirigimos al dashboard o panel principal (ejemplo: 'dashboard')
                return redirect('gestion_enfermeros')  # Cambia por la URL de tu pantalla principal
            else:
                messages.error(
                    request,
                    'Contraseña incorrecta. Por favor, verifique sus datos.',
                )
        else:
            messages.error(
                request,
                'No se encontró ningún enfermero registrado con ese DNI o correo.',
            )

    return render(request, 'Login_Usuario.html')

#? Cerrar sesión del usuario
def cerrar_sesion(request):
  request.session.flush()  # Borra toda la sesión del usuario
  messages.info(request, 'Has cerrado sesión correctamente.')
  return redirect('login_usuario')  # Redirige a tu vista de login



def mostrar_home(request):
    return render(request, 'Home.html')

def mostrar_pacientes(request):
    return render(request, 'Gestion_Pacientes.html')

def mostrar_enfermeros(request):
    return render(request, 'Gestion_Enfermeros.html')


# Controladores para la gestión de camas y sectores
def mostrar_sector_camas(request):
  datos_sectores = {}

  # Buscamos los dos sectores fijos por su código
  for codigo_sector in ['varones', 'mujeres']:
    sector = Sector.objects.filter(codigo=codigo_sector).first()

    habitaciones_list = []
    nombre_sector = ('Sector ' + codigo_sector.capitalize() ) 

    if sector:
      nombre_sector = sector.nombre
      for hab in sector.habitaciones.all():
        camas_list = []
        for cama in hab.camas.all():
          paciente_nombre = None
          paciente_dni = None
          paciente_diag = None

          if cama.paciente:
            paciente_nombre = (
                f'{cama.paciente.nombre} {cama.paciente.apellido}'
            )
            paciente_dni = cama.paciente.dni
            paciente_diag = cama.paciente.diagnostico

          camas_list.append({
              'id': cama.id,  # <-- Necesario para liberar o asignar
              'numero': cama.nombre,
              'estado': cama.estado,
              'paciente': paciente_nombre,
              'paciente_id': cama.paciente.id if cama.paciente else None,  # <-- Necesario para /planillas/{id}
              'dni': paciente_dni,
              'diag': paciente_diag,
          })

        habitaciones_list.append(
            {'habitacion': hab.nombre, 'camas': camas_list}
        )

    # Guardamos con la clave exacta ('varones' o 'mujeres')
    datos_sectores[codigo_sector] = {
        'nombre': nombre_sector,
        'habitaciones': habitaciones_list,
    }
    
  # FILTRAR SOLO PACIENTES QUE NO TIENEN CAMA ASIGNADA
  pacientes_libres = Paciente.objects.filter(cama_asignada__isnull=True)

  context = {
      'datos_sectores_json': datos_sectores,
      'pacientes_libres': pacientes_libres,
  }

  return render(request, 'Sector_Camas.html', context)

# Vista para liberar una cama ocupada
def liberar_cama_view(request, cama_id):
    # Buscamos la cama o devolvemos 404 si no existe
    cama = get_object_or_404(Cama, id=cama_id)
    
    # Liberamos la cama (dependiendo de cómo lo maneje tu modelo)
    cama.paciente = None   #* Esto libera la cama al desvincular el paciente
    cama.save()
    
    # Redirigimos de vuelta a la vista de sectores y camas
    return redirect('sector_camas') # Asegúrate de usar el nombre de tu URL actual

# NUEVA VISTA PARA PROCESAR LA ASIGNACIÓN
def asignar_paciente_view(request, cama_id):
  if request.method == 'POST':
    cama = get_object_or_404(Cama, id=cama_id)
    paciente_id = request.POST.get('paciente_id')

    if paciente_id:
      paciente = get_object_or_404(Paciente, id=paciente_id)
      cama.paciente = paciente
      cama.save()

  return redirect('sector_camas')  # Reemplaza con el nombre de tu URL actual para esta vista



def mostrar_planillas(request):
    return render(request, 'Planillas.html')

