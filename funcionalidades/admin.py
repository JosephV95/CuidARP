from django.contrib import admin

# Importo el modelo de Enfermero para poder registrarlo en el panel de administración
from .models import Enfermero, Paciente, Sector, Habitacion, Cama
from .models import Receta, MedicacionReceta, RegistroAdministracion

# Register your models here.
admin.site.register(Enfermero)  # Esto permite que el modelo Enfermero sea visible y editable en el panel de administración de Django
admin.site.register(Paciente)  # Esto permite que el modelo Paciente sea visible y editable en el panel de administración de Django
admin.site.register(Sector)
admin.site.register(Habitacion)
admin.site.register(Cama)

# Tablas de administración para las planillas

admin.site.register(Receta)
admin.site.register(MedicacionReceta)
admin.site.register(RegistroAdministracion)