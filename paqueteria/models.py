from django.db import models

class Sucursal(models.Model):
    nombre = models.CharField(max_length=100)
    estado = models.CharField(max_length=50)
    direccion = models.CharField(max_length=100)
    rfc = models.CharField(max_length=50)
    codigo_postal = models.CharField(max_length=10)
    numero_telefonico = models.CharField(max_length=15)
    atendio = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre


class InicioLogin(models.Model):
    usuario = models.CharField(max_length=50)
    clave = models.CharField(max_length=50)
    sucursal = models.ForeignKey(Sucursal, db_column='id_sucursal', on_delete=models.CASCADE)

    def __str__(self):
        return self.usuario
    
    class Meta:
        db_table = 'InicioLogin'


class Envio(models.Model):
    fecha = models.DateField()
    remitente = models.CharField(max_length=100)
    num_telefonico = models.CharField(max_length=15)
    contenido = models.TextField(max_length=2000)
    destinatario = models.CharField(max_length=200)
    codigo_postal = models.CharField(max_length=10)
    direccion_destino = models.CharField(max_length=250)
    referencias_destino = models.TextField(max_length=3500)
    medida_ancho = models.DecimalField(max_digits=10, decimal_places=2)
    medida_alto = models.DecimalField(max_digits=10, decimal_places=2)
    medida_largo = models.DecimalField(max_digits=10, decimal_places=2)
    peso = models.DecimalField(max_digits=10, decimal_places=2)
    paqueteria = models.CharField(max_length=100)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)

    def __str__(self):
        return f"Envío #{self.id}"


class Devolucion(models.Model):
    nombre_cliente = models.CharField(max_length=100)
    fecha_entrega = models.DateField()
    hora_entrega = models.TimeField()
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)

    def __str__(self):
        return f"Devolución de {self.nombre_cliente}"

