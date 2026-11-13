from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages  # Para mostrar alertas amigables
# import json  # Para convertir datos de Python a JSON y enviarlos al template

# Importar los modelos de la app funcionalidades
from .models import Enfermero, Paciente, Sector, Cama, Receta, RegistroAdministracion

# Create your views here.


# * Controladores para el login y el logout de usuarios --------------------------------------
def mostrar_registro_usuario(request):
    if request.method == "POST":
        # 1 Capturamos los datos enviados desde el formulario HTML
        nombre_form = request.POST.get(
            "nombre", " "
        )  # Valor por defecto vacío si no se encuentra
        apellido_form = request.POST.get(
            "apellido", " "
        )  # Valor por defecto vacío si no se encuentra
        dni_form = request.POST.get(
            "dni", " "
        )  # Valor por defecto vacío si no se encuentra
        matricula_form = request.POST.get("matricula", " ")
        telefono_form = request.POST.get("telefono", " ")
        email_form = request.POST.get("email", " ")
        tipo_prof_form = request.POST.get("tipo_profesional", " ")
        servicio_form = request.POST.get("servicio", " ")
        rol_form = request.POST.get("rol", " ")
        pin_form = request.POST.get("pin_sello", " ")
        password_form = request.POST.get(
            "password", " "
        )  # Nota: A futuro lo ideal es encriptarla

        # 2 Validamos de forma unificada si ya existe DNI, Email o Matrícula
        error_encontrado = False

        # Validar si ya existe un enfermero con el mismo DNI o Email
        if Enfermero.objects.filter(dni=dni_form).exists():
            messages.error(
                request,
                "El DNI ingresado ya se encuentra registrado en el sistema.",
            )
            error_encontrado = True

        if Enfermero.objects.filter(email=email_form).exists():
            messages.error(
                request,
                "El correo electrónico ingresado ya está en uso por otro profesional.",
            )
            error_encontrado = True

        if Enfermero.objects.filter(matricula=matricula_form).exists():
            messages.error(
                request, "El número de matrícula ingresado ya está registrado."
            )
            error_encontrado = True

        # 3. Si hubo CUALQUIER error, devolvemos el template UNA SOLA VEZ con los datos
        if error_encontrado:
            return render(
                request,
                "Registro_Usuario.html",
                {
                    "nombre": nombre_form,
                    "apellido": apellido_form,
                    "dni": dni_form,
                    "matricula": matricula_form,
                    "telefono": telefono_form,
                    "email": email_form,
                    "tipo_profesional": tipo_prof_form,
                    "servicio": servicio_form,
                    "rol": rol_form,
                    "pin_sello": pin_form,
                    "password": password_form,  # La contraseña por seguridad suele limpiarse, pero puedes pasarla si deseas
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
            "¡Registro exitoso! Su cuenta ha sido creada pero se encuentra"
            " pendiente de aprobación por un superior.",
        )
        # Redirigimos al LOGIN como bien sugeriste, no al home
        return redirect("login_usuario")

    else:  # Si la petición es GET, simplemente mostramos el formulario vacío
        return render(request, "Registro_Usuario.html")


# ? Autenticacion del usuario (login)
def mostrar_login_usuario(request):
    if request.method == "POST":
        identificador = request.POST.get(
            "username"
        )  # Puede ser DNI o Correo Electrónico
        password_ingresada = request.POST.get("password")

        # Buscamos al enfermero por DNI o por Email
        enfermero = (
            Enfermero.objects.filter(dni=identificador).first()
            or Enfermero.objects.filter(email=identificador).first()
        )

        if enfermero:
            # Verificamos la contraseña
            if enfermero.password == password_ingresada:
                # 1. VALIDACIÓN CLAVE: ¿Está verificado por el Jefe de Enfermeros?
                if not enfermero.verificado:
                    messages.warning(
                        request,
                        "Su cuenta se encuentra pendiente de aprobación por un Jefe de"
                        " Enfermeros.",
                    )
                    return render(request, "Login_Usuario.html")

                # 2. CREAMOS LA SESIÓN: Guardamos los datos clave en la sesión del navegador
                request.session["enfermero_id"] = enfermero.id
                request.session["nombre"] = enfermero.nombre
                request.session["apellido"] = enfermero.apellido
                request.session["nombre_completo"] = (
                    f"{enfermero.nombre} {enfermero.apellido}"
                )
                request.session["rol"] = enfermero.rol
                request.session["servicio"] = enfermero.servicio

                messages.success(request, f"¡Bienvenido/a, {enfermero.nombre}!")

                # 3. Redirigimos al dashboard o panel principal (ejemplo: 'dashboard')
                if request.session["rol"] == "jefe":
                    return redirect(
                        "gestion_enfermeros"
                    )  # Redirige a la gestión de enfermeros
                else:
                    return redirect(
                        "sector_camas"
                    )  # Cambia por la URL de tu pantalla principal
            else:
                messages.error(
                    request,
                    "Contraseña incorrecta. Por favor, verifique sus datos.",
                )
        else:
            messages.error(
                request,
                "No se encontró ningún enfermero registrado con ese DNI o correo.",
            )

    return render(request, "Login_Usuario.html")


# ? Cerrar sesión del usuario
def cerrar_sesion(request):
    # 1. Limpiamos cualquier mensaje acumulado previamente en el storage
    storage = messages.get_messages(request)
    storage.used = (
        True  # Esto marca todos los mensajes pendientes como ya leídos/ignorados
    )

    # 2. Borramos toda la sesión del usuario (esto también vaciará el storage actual)
    request.session.flush()
    # 3. Agregamos únicamente el mensaje limpio de cierre de sesión
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect("login_usuario")  # Redirige a tu vista de login


# * ---------------------


def mostrar_home(request):
    return render(request, "Home.html")


# * Controlador para mostrar la gestión de pacientes --------------------------

def gestion_pacientes_view(request):
    # 1. Consultamos todos los pacientes registrados en la base de datos
    pacientes_qs = Paciente.objects.all().order_by("-fecha_registro")

    pacientes_list = []
    for p in pacientes_qs:
        # Generar iniciales para el avatar
        iniciales = (
            f"{p.nombre[0]}{p.apellido[0]}".upper() if p.nombre and p.apellido else "PA"
        )

        # Obtenemos la cama asignada (si tiene una vinculada en la base de datos)
        cama_obj = p.cama_asignada.first()
        if cama_obj:
            sector_nombre = cama_obj.habitacion.sector.nombre
            habitacion_nombre = cama_obj.habitacion.nombre
            cama_nombre = cama_obj.nombre
        else:
            sector_nombre = "Sin Sector"
            habitacion_nombre = "--"
            cama_nombre = "Sin Cama Asignada"

        # Obtenemos las recetas asociadas al paciente
        recetas_list = []
        for r in p.recetas.all():
            meds_list = []
            for m in r.medicaciones.all():
                meds_list.append(
                    {
                        "farmaco": m.farmaco,
                        "dosis": m.dosis,
                        "via": m.via,
                        "frecuencia": m.frecuencia,
                        "observaciones": m.observaciones or "--",
                    }
                )

            recetas_list.append(
                {
                    "idReceta": r.id,  # o r.numero_receta
                    "numero_receta": r.numero_receta,
                    "fecha": r.fecha.strftime("%d/%m/%Y"),
                    "medico": r.medico_prescriptor,
                    "estado": r.estado,
                    "medicaciones": meds_list,
                }
            )

        # Estructura del paciente adaptada al JSON que consume tu JS
        pacientes_list.append(
            {
                "id": p.id,
                "nombre": p.nombre,
                "apellido": p.apellido,
                "dni": p.dni,
                "fecha_nacimiento": (
                    p.fecha_nacimiento.strftime("%Y-%m-%d")
                    if p.fecha_nacimiento
                    else ""
                ),
                "fechaNacimientoDisplay": (
                    p.fecha_nacimiento.strftime("%d/%m/%Y")
                    if p.fecha_nacimiento
                    else ""
                ),
                "email": p.email or "",
                "obra_social": p.obra_social,
                "sexo_paciente": p.sexo_paciente,
                "telefono": p.telefono,
                "direccion": p.direccion,
                "estado_paciente": p.estado_paciente,
                "estadoBadge": (
                    "bg-emerald-100 text-emerald-800 border-emerald-200"
                    if p.estado_paciente == "Internado"
                    else "bg-blue-100 text-blue-800 border-blue-200"
                ),
                "diagnostico": p.diagnostico,
                "sector": sector_nombre,
                "habitacion": habitacion_nombre,
                "cama": cama_nombre,
                "avatar": iniciales,
                "avatarBg": (
                    "bg-sky-100 text-sky-800"
                    if p.estado_paciente == "Internado"
                    else "bg-purple-100 text-purple-800"
                ),
                "recetas": recetas_list,
            }
        )

    context = {
        "pacientes_list": pacientes_list,
    }
    return render(request, "Gestion_de_pacientes.html", context)


# Crear Paciente
def crear_paciente_view(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        apellido = request.POST.get("apellido")
        dni = request.POST.get("dni")
        fecha_nacimiento = request.POST.get("fecha_nacimiento")
        email = request.POST.get("email") or None
        obra_social = request.POST.get("obra_social")
        telefono = request.POST.get("telefono")
        direccion = request.POST.get("direccion")
        sexo_paciente = request.POST.get("sexo_paciente")
        estado_paciente = request.POST.get("estado_paciente")
        diagnostico = request.POST.get("diagnostico")

        Paciente.objects.create(
            nombre=nombre,
            apellido=apellido,
            dni=dni,
            fecha_nacimiento=fecha_nacimiento,
            email=email,
            obra_social=obra_social,
            telefono=telefono,
            direccion=direccion,
            sexo_paciente=sexo_paciente,
            estado_paciente=estado_paciente,
            diagnostico=diagnostico,
        )
        messages.success(request, f"Paciente {nombre} {apellido} creado con éxito.")
    return redirect("gestion_pacientes")


# Editar Paciente
def editar_paciente_view(request, paciente_id):
    if request.method == "POST":
        paciente = get_object_or_404(Paciente, id=paciente_id)
        paciente.nombre = request.POST.get("nombre")
        paciente.apellido = request.POST.get("apellido")
        paciente.dni = request.POST.get("dni")
        paciente.fecha_nacimiento = request.POST.get("fecha_nacimiento")
        paciente.email = request.POST.get("email") or None
        paciente.obra_social = request.POST.get("obra_social")
        paciente.telefono = request.POST.get("telefono")
        paciente.direccion = request.POST.get("direccion")
        paciente.sexo_paciente = request.POST.get("sexo_paciente")
        paciente.estado_paciente = request.POST.get("estado_paciente")
        paciente.diagnostico = request.POST.get("diagnostico")
        paciente.save()

        messages.success(
            request,
            f"Ficha clínica de {paciente.nombre} {paciente.apellido} actualizada.",
        )
    return redirect("gestion_pacientes")


# * Controlador para mostrar la gestión de enfermeros --------------------------
def mostrar_enfermeros(request):
    # 1. Validación de seguridad y rol (Si no es jefe de enfermeros, deniega el acceso)
    # Adaptar 'request.session' o 'request.user' según tu sistema de sesión actual
    rol_usuario = request.session.get("rol", "")
    if rol_usuario != "jefe":
        messages.error(
            request, "Acceso denegado: Se requieren permisos de Jefe de Enfermeros."
        )
        # Pasa lista vacía para que el HTML muestre el mensaje de aviso/error
        context = {
            "enfermeros_list": [],
            "es_jefe": False,
        }
        return render(request, "Gestion_Enfermeros.html", context)

    # 2. Obtenemos solo la nómina activa de enfermeros (baja lógica: activo=True)
    enfermeros_qs = Enfermero.objects.filter(activo=True).order_by("-fecha_registro")

    # 3. Serializamos la lista a un diccionario para pasarlo limpiamente al frontend
    enfermeros_list = []
    for enf in enfermeros_qs:
        # Generar iniciales para el avatar
        iniciales = (
            f"{enf.nombre[0]}{enf.apellido[0]}".upper()
            if enf.nombre and enf.apellido
            else "EN"
        )

        enfermeros_list.append(
            {
                "id": enf.id,
                "nombre": f"{enf.nombre} {enf.apellido}",
                "dni": enf.dni,
                "matricula": enf.matricula,
                "email": enf.email,
                "telefono": enf.telefono,
                "puesto": enf.tipo_profesional,
                "servicioHospital": enf.servicio,
                "verificado": enf.verificado,
                "sisa": {
                    "especialidad": (
                        f"{enf.tipo_profesional} registrado en Salud Mental"
                    )
                },
                "avatar": iniciales,
                "avatarBg": (
                    "bg-emerald-100 text-emerald-800"
                    if enf.verificado
                    else "bg-amber-100 text-amber-800"
                ),
            }
        )

    context = {
        # ¡Pásalo como lista de Python pura, sin json.dumps!
        "enfermeros_list": enfermeros_list,
        "es_jefe": True,
    }
    return render(request, "Gestion_Enfermeros.html", context)


# Endpoint: Aprobar / Verificar Cuenta de Enfermero
def aprobar_enfermero_view(request, enfermero_id):
    if request.method == "POST" or request.method == "GET":
        enfermero = get_object_or_404(Enfermero, id=enfermero_id)
        enfermero.verificado = True
        enfermero.save()
    return redirect("gestion_enfermeros")


# Endpoint: Dar de baja lógica (Conservando registros históricos)
def dar_baja_enfermero_view(request, enfermero_id):
    if request.method == "POST" or request.method == "GET":
        enfermero = get_object_or_404(Enfermero, id=enfermero_id)
        enfermero.activo = False  # Baja lógica
        enfermero.save()
    return redirect("gestion_enfermeros")


# * Controladores para la gestión de camas y sectores --------------------------
def mostrar_sector_camas(request):
    datos_sectores = {}

    # Buscamos los dos sectores fijos por su código
    for codigo_sector in ["varones", "mujeres"]:
        sector = Sector.objects.filter(codigo=codigo_sector).first()

        habitaciones_list = []
        nombre_sector = "Sector " + codigo_sector.capitalize()

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
                            f"{cama.paciente.nombre} {cama.paciente.apellido}"
                        )
                        paciente_dni = cama.paciente.dni
                        paciente_diag = cama.paciente.diagnostico

                    camas_list.append(
                        {
                            "id": cama.id,  # <-- Necesario para liberar o asignar
                            "numero": cama.nombre,
                            "estado": cama.estado,
                            "paciente": paciente_nombre,
                            "paciente_id": cama.paciente.id
                            if cama.paciente
                            else None,  # <-- Necesario para /planillas/{id}
                            "dni": paciente_dni,
                            "diag": paciente_diag,
                        }
                    )

                habitaciones_list.append(
                    {"habitacion": hab.nombre, "camas": camas_list}
                )

        # Guardamos con la clave exacta ('varones' o 'mujeres')
        datos_sectores[codigo_sector] = {
            "nombre": nombre_sector,
            "habitaciones": habitaciones_list,
        }

    # FILTRAR SOLO PACIENTES QUE NO TIENEN CAMA ASIGNADA
    pacientes_libres = Paciente.objects.filter(cama_asignada__isnull=True)

    context = {
        "datos_sectores_json": datos_sectores,
        "pacientes_libres": pacientes_libres,
    }

    return render(request, "Sector_Camas.html", context)


# ? Vista para liberar una cama ocupada
def liberar_cama_view(request, cama_id):
    # Buscamos la cama o devolvemos 404 si no existe
    cama = get_object_or_404(Cama, id=cama_id)

    # Liberamos la cama (dependiendo de cómo lo maneje tu modelo)
    cama.paciente = None  # * Esto libera la cama al desvincular el paciente
    cama.save()

    # Redirigimos de vuelta a la vista de sectores y camas
    return redirect("sector_camas")  # Asegúrate de usar el nombre de tu URL actual


# ? NUEVA VISTA PARA PROCESAR LA ASIGNACIÓN
def asignar_paciente_view(request, cama_id):
    if request.method == "POST":
        cama = get_object_or_404(Cama, id=cama_id)
        paciente_id = request.POST.get("paciente_id")

        if paciente_id:
            paciente = get_object_or_404(Paciente, id=paciente_id)
            cama.paciente = paciente
            cama.save()

    return redirect(
        "sector_camas"
    )  # Reemplaza con el nombre de tu URL actual para esta vista


# PRUEBAS PLANILLAS


def mostrar_planillas(request, paciente_id=None):
    # Si ingresan a /planillas/ sin ID, seleccionamos el primer paciente disponible automáticamente
    if paciente_id:
        paciente = get_object_or_404(Paciente, id=paciente_id)
    else:
        paciente = Paciente.objects.first()

    # Si de plano no hay ningún paciente registrado en la base de datos todavía
    if not paciente:
        messages.warning(
            request, "Debe registrar al menos un paciente para ver las planillas."
        )
        return redirect("gestion_pacientes")  # O a la vista que prefieras

    # Obtener las recetas activas exclusivamente de este paciente
    recetas = Receta.objects.filter(paciente=paciente, estado="Activo")
    recetas_json = [{"id": r.id, "numero_receta": r.numero_receta} for r in recetas]

    # Obtener los registros de administración de este paciente
    registros = RegistroAdministracion.objects.filter(paciente=paciente).order_by(
        "-fecha", "-id"
    )
    registros_json = [
        {
            "id": reg.id,
            "fecha": reg.fecha.strftime("%d/%m/%Y"),
            "numero_receta": reg.receta.numero_receta,
            "horarios": reg.horarios,
            "observaciones": reg.observaciones or "",
            "enfermero_nombre": f"{reg.enfermero.nombre} {reg.enfermero.apellido}",
            "enfermero_matricula": reg.enfermero.matricula,
        }
        for reg in registros
    ]

    return render(
        request,
        "Planillas.html",
        {
            "paciente": paciente,
            "recetas_paciente_json": recetas_json,
            "registros_json": registros_json,
        },
    )


def guardar_administracion(request, paciente_id):
    if request.method == "POST":
        paciente = get_object_or_404(Paciente, id=paciente_id)
        pin_ingresado = request.POST.get("pin_ingresado", "").strip()

        # Validar el PIN contra los enfermeros activos y verificados
        enfermero_firmante = None
        for enf in Enfermero.objects.filter(activo=True, verificado=True):
            if enf.pin_sello == pin_ingresado:
                enfermero_firmante = enf
                break

        if not enfermero_firmante:
            messages.error(
                request, "PIN incorrecto o no pertenece a un enfermero habilitado."
            )
            return redirect("gestion_planillas", paciente_id=paciente.id)

        horarios_nuevos = request.POST.getlist("horarios")
        receta_id = request.POST.get("receta_id")
        fecha = request.POST.get("fecha")
        observaciones = request.POST.get("observaciones", "").strip()

        # 1. BUSCAR SI YA EXISTE UN REGISTRO PARA ESTA RECETA Y ESTA FECHA
        registro_existente = RegistroAdministracion.objects.filter(
            paciente=paciente, receta_id=receta_id, fecha=fecha
        ).first()

        if registro_existente:
            # 2. SI EXISTE: Actualizamos combinando los horarios (evitando duplicados)
            horarios_actuales = (
                registro_existente.horarios
                if isinstance(registro_existente.horarios, list)
                else []
            )

            for h in horarios_nuevos:
                if h not in horarios_actuales:
                    horarios_actuales.append(h)

            registro_existente.horarios = horarios_actuales

            # Si se escribió una nueva observación, la reemplazamos
            if observaciones:
                registro_existente.observaciones = observaciones

            # Actualizamos también el último enfermero que firmó la modificación
            registro_existente.enfermero = enfermero_firmante
            registro_existente.save()

            messages.success(
                request,
                f"Se actualizaron los horarios de administración para la receta, firma"
                f" por {enfermero_firmante.nombre} {enfermero_firmante.apellido}.",
            )
        else:
            # 3. SI NO EXISTE: Creamos un registro completamente nuevo
            RegistroAdministracion.objects.create(
                paciente=paciente,
                receta_id=receta_id,
                fecha=fecha,
                horarios=horarios_nuevos,
                observaciones=observaciones,
                enfermero=enfermero_firmante,
            )

            messages.success(
                request,
                f"Administración registrada y firmada por {enfermero_firmante.nombre}"
                f" {enfermero_firmante.apellido}.",
            )

        return redirect("gestion_planillas", paciente_id=paciente.id)


def eliminar_administracion(request, registro_id):
    if request.method == "POST":
        registro = get_object_or_404(RegistroAdministracion, id=registro_id)
        paciente_id = registro.paciente.id  # Rescatamos el ID antes de borrar

        pin_ingresado = request.POST.get("pin_ingresado", "").strip()

        enfermero_autorizado = None
        for enf in Enfermero.objects.filter(activo=True, verificado=True):
            if enf.pin_sello == pin_ingresado:
                enfermero_autorizado = enf
                break

        if not enfermero_autorizado:
            messages.error(
                request, "PIN incorrecto. No se pudo autorizar la eliminación."
            )
            return redirect("gestion_planillas", paciente_id=paciente_id)

        registro.delete()
        messages.success(
            request,
            "El registro de administración ha sido eliminado correctamente.",
        )
        return redirect("gestion_planillas", paciente_id=paciente_id)
