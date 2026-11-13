from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages  # Para mostrar alertas amigables
from django.contrib.auth import authenticate, login, logout
import json  # Para convertir datos de Python a JSON y enviarlos al template

#Importar los modelos de la app funcionalidades
from .models import Enfermero, Paciente, Sector, Habitacion, Cama

# Create your views here.

#* Controladores para el login y el logout de usuarios --------------------------------------
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
                if request.session['rol'] == 'jefe':
                    return redirect('gestion_enfermeros')  # Redirige a la gestión de enfermeros
                else:
                    return redirect('sector_camas')  # Cambia por la URL de tu pantalla principal
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
  # 1. Limpiamos cualquier mensaje acumulado previamente en el storage
  storage = messages.get_messages(request)
  storage.used = (True ) # Esto marca todos los mensajes pendientes como ya leídos/ignorados

  # 2. Borramos toda la sesión del usuario (esto también vaciará el storage actual)
  request.session.flush()
  # 3. Agregamos únicamente el mensaje limpio de cierre de sesión
  messages.info(request, 'Has cerrado sesión correctamente.')
  return redirect('login_usuario')  # Redirige a tu vista de login

#* ---------------------


def mostrar_home(request):
    return render(request, 'Home.html')

def mostrar_pacientes(request):
    return render(request, 'Gestion_Pacientes.html')

#* Controlador para mostrar la gestión de enfermeros --------------------------
def mostrar_enfermeros(request):
  # 1. Validación de seguridad y rol (Si no es jefe de enfermeros, deniega el acceso)
  # Adaptar 'request.session' o 'request.user' según tu sistema de sesión actual
  rol_usuario = request.session.get('rol', '')
  if rol_usuario != 'jefe':
    messages.error(
        request, 'Acceso denegado: Se requieren permisos de Jefe de Enfermeros.'
    )
    # Pasa lista vacía para que el HTML muestre el mensaje de aviso/error
    context = {
        'enfermeros_list': [],
        'es_jefe': False,
    }
    return render(request, 'Gestion_Enfermeros.html', context)

  # 2. Obtenemos solo la nómina activa de enfermeros (baja lógica: activo=True)
  enfermeros_qs = Enfermero.objects.filter(activo=True).order_by(
      '-fecha_registro'
  )

  # 3. Serializamos la lista a un diccionario para pasarlo limpiamente al frontend
  enfermeros_list = []
  for enf in enfermeros_qs:
    # Generar iniciales para el avatar
    iniciales = (
        f'{enf.nombre[0]}{enf.apellido[0]}'.upper()
        if enf.nombre and enf.apellido
        else 'EN'
    )

    enfermeros_list.append({
        'id': enf.id,
        'nombre': f'{enf.nombre} {enf.apellido}',
        'dni': enf.dni,
        'matricula': enf.matricula,
        'email': enf.email,
        'telefono': enf.telefono,
        'puesto': enf.tipo_profesional,
        'servicioHospital': enf.servicio,
        'verificado': enf.verificado,
        'sisa': {
            'especialidad': (
                f'{enf.tipo_profesional} registrado en Salud Mental'
            )
        },
        'avatar': iniciales,
        'avatarBg': (
            'bg-emerald-100 text-emerald-800'
            if enf.verificado
            else 'bg-amber-100 text-amber-800'
        ),
    })

  context = {
      # ¡Pásalo como lista de Python pura, sin json.dumps!
      'enfermeros_list': enfermeros_list,
      'es_jefe': True,
  }
  return render(request, 'Gestion_Enfermeros.html', context)


# Endpoint: Aprobar / Verificar Cuenta de Enfermero
def aprobar_enfermero_view(request, enfermero_id):
  if request.method == 'POST' or request.method == 'GET':
    enfermero = get_object_or_404(Enfermero, id=enfermero_id)
    enfermero.verificado = True
    enfermero.save()
  return redirect('gestion_enfermeros')


# Endpoint: Dar de baja lógica (Conservando registros históricos)
def dar_baja_enfermero_view(request, enfermero_id):
  if request.method == 'POST' or request.method == 'GET':
    enfermero = get_object_or_404(Enfermero, id=enfermero_id)
    enfermero.activo = False  # Baja lógica
    enfermero.save()
  return redirect('gestion_enfermeros')




#* Controladores para la gestión de camas y sectores --------------------------
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

#? Vista para liberar una cama ocupada
def liberar_cama_view(request, cama_id):
    # Buscamos la cama o devolvemos 404 si no existe
    cama = get_object_or_404(Cama, id=cama_id)
    
    # Liberamos la cama (dependiendo de cómo lo maneje tu modelo)
    cama.paciente = None   #* Esto libera la cama al desvincular el paciente
    cama.save()
    
    # Redirigimos de vuelta a la vista de sectores y camas
    return redirect('sector_camas') # Asegúrate de usar el nombre de tu URL actual

#? NUEVA VISTA PARA PROCESAR LA ASIGNACIÓN
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



#PRUEBAS PLANILLAS 
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Paciente, Receta, RegistroAdministracion, Enfermero

def mostrar_planillas(request, paciente_id=None):
    # Si ingresan a /planillas/ sin ID, seleccionamos el primer paciente disponible automáticamente
    if paciente_id:
        paciente = get_object_or_404(Paciente, id=paciente_id)
    else:
        paciente = Paciente.objects.first()
        
    # Si de plano no hay ningún paciente registrado en la base de datos todavía
    if not paciente:
        messages.warning(request, "Debe registrar al menos un paciente para ver las planillas.")
        return redirect('gestion_pacientes') # O a la vista que prefieras

    # Obtener las recetas activas exclusivamente de este paciente
    recetas = Receta.objects.filter(paciente=paciente, estado='Activo')
    recetas_json = [
        {'id': r.id, 'numero_receta': r.numero_receta} 
        for r in recetas
    ]
    
    # Obtener los registros de administración de este paciente
    registros = RegistroAdministracion.objects.filter(paciente=paciente).order_by('-fecha', '-id')
    registros_json = [
        {
            'id': reg.id,
            'fecha': reg.fecha.strftime('%d/%m/%Y'),
            'numero_receta': reg.receta.numero_receta,
            'horarios': reg.horarios,
            'observaciones': reg.observaciones or '',
            'enfermero_nombre': f"{reg.enfermero.nombre} {reg.enfermero.apellido}",
            'enfermero_matricula': reg.enfermero.matricula,
        }
        for reg in registros
    ]

    return render(request, 'Planillas.html', {
        'paciente': paciente,
        'recetas_paciente_json': recetas_json,
        'registros_json': registros_json,
    })
    
    from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Paciente, Enfermero, RegistroAdministracion

def guardar_administracion(request, paciente_id):
    if request.method == 'POST':
        paciente = get_object_or_404(Paciente, id=paciente_id)
        pin_ingresado = request.POST.get('pin_ingresado', '').strip()
        
        # Validar el PIN contra los enfermeros activos y verificados
        enfermero_firmante = None
        for enf in Enfermero.objects.filter(activo=True, verificado=True):
            if enf.pin_sello == pin_ingresado:
                enfermero_firmante = enf
                break

        if not enfermero_firmante:
            messages.error(request, "PIN incorrecto o no pertenece a un enfermero habilitado.")
            return redirect('gestion_planillas')

        horarios_lista = request.POST.getlist('horarios')
        receta_id = request.POST.get('receta_id')
        fecha = request.POST.get('fecha')
        observaciones = request.POST.get('observaciones', '')

        RegistroAdministracion.objects.create(
            paciente=paciente,
            receta_id=receta_id,
            fecha=fecha,
            horarios=horarios_lista,
            observaciones=observaciones,
            enfermero=enfermero_firmante
        )
        
        messages.success(request, f"Administración registrada y firmada por {enfermero_firmante.nombre} {enfermero_firmante.apellido}.")
        return redirect('gestion_planillas')


def eliminar_administracion(request, registro_id):
    if request.method == 'POST':
        registro = get_object_or_404(RegistroAdministracion, id=registro_id)
        pin_ingresado = request.POST.get('pin_ingresado', '').strip()
        
        # Validar el PIN para autorizar la eliminación
        enfermero_autorizado = None
        for enf in Enfermero.objects.filter(activo=True, verificado=True):
            if enf.pin_sello == pin_ingresado:
                enfermero_autorizado = enf
                break

        if not enfermero_autorizado:
            messages.error(request, "PIN incorrecto. No se pudo autorizar la eliminación.")
            return redirect('gestion_planillas')

        registro.delete()
        messages.success(request, "El registro de administración ha sido eliminado correctamente.")
        return redirect('gestion_planillas')
    