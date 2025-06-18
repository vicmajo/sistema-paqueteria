from django.contrib import admin
from .models import Sucursal, InicioLogin, Envio, Devolucion

admin.site.register(Sucursal)
admin.site.register(InicioLogin)
admin.site.register(Envio)
admin.site.register(Devolucion)
