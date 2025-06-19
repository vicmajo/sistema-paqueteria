from django.db import connection
from django.shortcuts import render, redirect

from gestionpaqueteria import settings
from .models import Sucursal, InicioLogin
import pyodbc # type: ignore


def obtener_nombres_sucursales():
    with connection.cursor() as cursor:
        cursor.execute('EXEC ObtenerNombresSucursales')
        results = cursor.fetchall()
        print("Resultados del SP:", results)
        sucursales = [{'id': row[0], 'nombre': row[1]} for row in results]
    return sucursales

def login_view(request):
    if request.method == 'POST':
        sucursal_id = request.POST.get('sucursal_id')
        usuario = request.POST.get('usuario', '').strip()
        contrasena = request.POST.get('contrasena', '').strip()

        request.session['usuario'] = usuario
        request.session['clave'] = contrasena
        request.session['id_sucursal'] = sucursal_id

        nombre_sucursal = obtener_nombre_sucursal_por_id(sucursal_id)
        request.session['nombre_sucursal'] = nombre_sucursal

        

        print(f"Usuario recibido: {usuario}")
        print(f"Contraseña recibida: {contrasena}")
        print(f"Sucursal seleccionada: {sucursal_id}")
        print(f"Sucursal seleccionada: {nombre_sucursal}")

        if sucursal_id:
            sucursal_id = int(sucursal_id)
        else:
            return render(request, 'paqueteria/login.html', {
                'error': 'Por favor seleccione una sucursal',
                'sucursales': obtener_nombres_sucursales()
            })

        login = InicioLogin.objects.filter(
            sucursal_id=sucursal_id,
            usuario=usuario,
            clave=contrasena
        ).first()

        print(f"Resultado del login: {login}")

        if login:
            request.session['usuario_id'] = login.id
            request.session['id_sucursal'] = sucursal_id

            nombre_sucursal = obtener_nombre_sucursal_por_id(sucursal_id)
            request.session['nombre_sucursal'] = nombre_sucursal

            request.session['usuario'] = usuario
            request.session['clave'] = contrasena


            return redirect('menu')
        else:
            return render(request, 'paqueteria/login.html', {
                'error': 'Credenciales incorrectas',
                'sucursales': obtener_nombres_sucursales()
            })

    sucursales = obtener_nombres_sucursales()
    

    return render(request, 'paqueteria/login.html', {'sucursales': sucursales})


# def login_view(request):
#     if request.method == 'POST':
#         sucursal_id = request.POST.get('sucursal_id')
#         if sucursal_id:
#             sucursal_id = int(sucursal_id)
#         else:
#             return render(request, 'paqueteria/login.html', {
#                 'error': 'Por favor seleccione una sucursal',
#                 'sucursales': obtener_nombres_sucursales()
#                 })
         
#         usuario = request.POST.get('usuario', '').strip()
#         contrasena = request.POST.get('contrasena', '').strip()


#         try:
#             login = InicioLogin.objects.get(usuario=usuario, clave=contrasena, sucursal_id=sucursal_id)
#             request.session['usuario_id'] = login.id
#             return redirect('menu')
#         except InicioLogin.DoesNotExist:
#             return render(request, 'paqueteria/login.html', {
#                 'error': 'Credenciales incorrectas', 
#                 'sucursales': obtener_nombres_sucursales()
#                 })
#     sucursales = obtener_nombres_sucursales()
#     return render(request, 'paqueteria/login.html', {'sucursales': sucursales})


# def menu_principal(request):
#     return render(request, 'paqueteria/menu.html')


from django.db import connection

def obtener_nombre_sucursal_por_id(sucursal_id):
    with connection.cursor() as cursor:
        cursor.execute('EXEC ObtenerNombreSucursalPorId @idSucursal=%s', [sucursal_id])
        resultado = cursor.fetchone()
        if resultado:
            return resultado[0]  
        return None



def menu_principal(request):
    id_sucursal = request.session.get('id_sucursal')
    print("ID Sucursal desde sesión:", id_sucursal)
    nombre_paqueteria = obtener_nombre_sucursal_por_id(id_sucursal)

    return render(request, 'paqueteria/menu.html', {
        'nombre_paqueteria': nombre_paqueteria
    })



def registrar_envio(request):
    return render(request, 'paqueteria/envio.html')



from django.shortcuts import render, redirect
from django.db import connection
from datetime import datetime

def registrar_devolucion(request):
    if request.method == 'POST':
        nombre_cliente = request.POST.get('nombre_cliente')
        fecha_entrega = request.POST.get('fecha_entrega')
        hora_entrega = request.POST.get('hora_entrega')
        id_sucursal = request.session.get('id_sucursal')

        accion = request.POST.get('accion')
        nombre_sucursal = request.session.get('nombre_sucursal')
        if not nombre_sucursal and id_sucursal:
            nombre_sucursal = obtener_nombre_sucursal_por_id(id_sucursal)

        if accion == 'guardar_imprimir':
            # Guardar registro en BD mediante procedimiento almacenado
            with connection.cursor() as cursor:
                cursor.execute('EXEC InsertarDevolucion @NombreCliente=%s, @FechaEntrega=%s, @HoraEntrega=%s, @idSucursal=%s',
                               [nombre_cliente, fecha_entrega, hora_entrega, id_sucursal])



        # with connection.cursor() as cursor:
        #     cursor.execute('EXEC InsertarDevolucion @NombreCliente=%s, @FechaEntrega=%s, @HoraEntrega=%s, @idSucursal=%s', 
        #                    [nombre_cliente, fecha_entrega, hora_entrega, id_sucursal])
        
        # Puedes redirigir o mostrar el ticket con los datos
        return render(request, 'paqueteria/ticket_devolucion.html', {
            'nombre_cliente': nombre_cliente,
            'fecha_entrega': fecha_entrega,
            'hora_entrega': hora_entrega,
            'paqueteria': nombre_sucursal,
            #'paqueteria': request.session.get('nombre_sucursal', 'Sucursal desconocida'),
        })

    return render(request, 'paqueteria/devolucion.html')

# def registrar_devolucion(request):
#     return render(request, 'paqueteria/envio.html')

def obtener_datos_sucursal_por_usuario(usuario):
    with connection.cursor() as cursor:
        cursor.execute('EXEC ObtenerDatosSucursalPorUsuario @usuario=%s', [usuario])
        resultado = cursor.fetchone()
        if resultado:
            return {
                'id': resultado[0],
                'nombre': resultado[1],
                'estado': resultado[2],
                'direccion': resultado[3],
                'rfc': resultado[4],
                'codigo_postal': resultado[5],
                'telefono': resultado[6],
                'atendio': resultado[7],
            }
    return None






def registrar_envio(request):
    usuario = request.session.get('usuario')
    datos_sucursal = obtener_datos_sucursal_por_usuario(usuario)

    if request.method == 'POST':
        accion = request.POST.get('accion')
        remitente = request.POST.get('remitente')
        telefono = request.POST.get('telefono')
        contenido = request.POST.get('contenido')
        destinatario = request.POST.get('destinatario')
        cp = request.POST.get('codigo_postal')
        direccion = request.POST.get('direccion')
        referencias = request.POST.get('referencias')
        ancho = request.POST.get('ancho')
        alto = request.POST.get('alto')
        largo = request.POST.get('largo')
        peso = request.POST.get('peso')
        paqueteria = request.POST.get('paqueteria')
        total = request.POST.get('total')

        id_sucursal = datos_sucursal['id'] if datos_sucursal else None

        if accion == 'guardar_imprimir':
            with connection.cursor() as cursor:
                cursor.execute('''
                    EXEC InsertarEnvio 
                        @fecha=%s, 
                        @Remitente=%s, 
                        @Num_Telefonico=%s, 
                        @Contenido=%s,
                        @Destinatario=%s,
                        @Codigo_postal=%s,
                        @Direccion_Destino=%s,
                        @Referencias_Destino=%s,
                        @Medida_Ancho=%s,
                        @Medida_Alto=%s,
                        @Medida_Largo=%s,
                        @Peso=%s,
                        @Paqueteria=%s,
                        @Total=%s,
                        @idSucursal=%s
                ''', [
                    datetime.now().date(), remitente, telefono, contenido,
                    destinatario, cp, direccion, referencias,
                    ancho, alto, largo, peso, paqueteria, total, id_sucursal
                ])

        return render(request, 'paqueteria/ticket_envio.html', {
            'datos_sucursal': datos_sucursal,
            'datos_envio': request.POST
        })

    return render(request, 'paqueteria/envio.html', {
        'datos_sucursal': datos_sucursal
    })



    
