from django.shortcuts import render

# Create your views here.
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

def mostrar_login_usuario(request):
    return render(request, 'Login_Usuario.html')
def mostrar_registro_usuario(request):
    return render(request, 'Registro_Usuario.html')