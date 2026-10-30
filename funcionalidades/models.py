from django.db import models

# Create your models here.

class Enfermero(models.Model):
  # Opciones para los select del formulario
  TIPO_PROFESIONAL_CHOICES = [
      ('Licenciado', 'Licenciado/a en Enfermería'),
      ('Enfermero Profesional', 'Enfermero/a Profesional'),
  ]

  SERVICIO_CHOICES = [
      ('Sector Varones', 'Sector Varones'),
      ('Sector Mujeres', 'Sector Mujeres'),
      ('Guardia / Admisión', 'Guardia / Admisión'),
      ('Internación General', 'Internación General'),
  ]

  ROL_CHOICES = [
      ('enfermero', 'Enfermero/a'),
      ('jefe', 'Jefe/a de Enfermeros'),
  ]

  # ! Campos basados en el formulario de registro
  
  nombre = models.CharField(max_length=100, verbose_name='Nombre')
  apellido = models.CharField(max_length=100, verbose_name='Apellido')
  dni = models.CharField(max_length=20, unique=True, verbose_name='DNI')
  matricula = models.CharField(
      max_length=50, unique=True, verbose_name='Matrícula SISA'
  )
  telefono = models.CharField(max_length=30, verbose_name='Teléfono')
  email = models.EmailField(
      unique=True, verbose_name='Correo Electrónico'
  )

  tipo_profesional = models.CharField(
      max_length=50,
      choices=TIPO_PROFESIONAL_CHOICES,
      verbose_name='Tipo de Profesional',
  )
  servicio = models.CharField(
      max_length=50,
      choices=SERVICIO_CHOICES,
      verbose_name='Servicio del Hospital',
  )
  rol = models.CharField(
      max_length=20, choices=ROL_CHOICES, verbose_name='Rol en la Plataforma'
  )

  pin_sello = models.CharField(
      max_length=4, verbose_name='PIN Numérico para Sello'
  )
  password = models.CharField(
      max_length=128, verbose_name='Contraseña'
  )  # Nota: A futuro se puede vincular al sistema de Auth de Django

  # Campo opcional para saber cuándo se registró
  fecha_registro = models.DateTimeField(
      auto_now_add=True, verbose_name='Fecha de Registro'
  )
  
  # Campo para indicar si la cuenta ha sido verificada.
  verificado = models.BooleanField(
      default=False, verbose_name='Cuenta Verificada'
  )

  def __str__(self):
    return (
        f'{self.apellido}, {self.nombre} - Mat: {self.matricula}'
        f' ({self.rol.upper()})'
    )