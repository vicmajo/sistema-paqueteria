from django.db import connection
from django.shortcuts import render, redirect
from datetime import datetime
from .models import Sucursal, InicioLogin


def obtener_nombres_sucursales():
    with connection.cursor() as cursor:
        cursor.execute('CALL ObtenerNombresSucursales()')
        results = cursor.fetchall()
        sucursales = [{'id': row[0], 'nombre': row[1]} for row in results]
    return sucursales


def obtener_nombre_sucursal_por_id(sucursal_id):
    with connection.cursor() as cursor:
        cursor.execute('CALL ObtenerNombreSucursalPorId(%s)', [sucursal_id])
        resultado = cursor.fetchone()
        if resultado:
            return resultado[0]
        return None


def obtener_datos_sucursal_por_usuario(usuario):
    with connection.cursor() as cursor:
        cursor.execute('CALL ObtenerDatosSucursalPorUsuario(%s)', [usuario])
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


def login_view(request):
    if request.method == 'POST':
        sucursal_id = request.POST.get('sucursal_id')
        usuario = request.POST.get('usuario', '').strip()
        contrasena = request.POST.get('contrasena', '').strip()

        if not sucursal_id:
            return render(request, 'paqueteria/login.html', {
                'error': 'Por favor seleccione una sucursal',
                'sucursales': obtener_nombres_sucursales()
            })

        sucursal_id = int(sucursal_id)

        nombre_sucursal = obtener_nombre_sucursal_por_id(sucursal_id)

        login = InicioLogin.objects.filter(
            sucursal_id=sucursal_id,
            usuario=usuario,
            clave=contrasena
        ).first()

        if login:
            request.session['usuario_id'] = login.id
            request.session['id_sucursal'] = sucursal_id
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


def menu_principal(request):
    id_sucursal = request.session.get('id_sucursal')
    nombre_paqueteria = obtener_nombre_sucursal_por_id(id_sucursal)

    return render(request, 'paqueteria/menu.html', {
        'nombre_paqueteria': nombre_paqueteria
    })


def registrar_envio(request):
    usuario = request.session.get('usuario')
    datos_sucursal = obtener_datos_sucursal_por_usuario(usuario)

    if request.method == 'POST':
        accion = request.POST.get('accion')
        if accion == 'regresar':
            return redirect('menu')

        remitente = request.POST.get('remitente')
        telefonoD = request.POST.get('telefonoD')
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
        numero_ticket = None

        if accion == 'guardar_imprimir':
            with connection.cursor() as cursor:
                cursor.execute('''
                    CALL InsertarEnvio(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', [
                    datetime.now().date(), remitente, telefonoD, contenido,
                    destinatario, cp, direccion, referencias,
                    ancho, alto, largo, peso, paqueteria, total, id_sucursal
                ])

                resultado = cursor.fetchone()
                if resultado:
                    numero_ticket = resultado[0]

        return render(request, 'paqueteria/ticket_envio.html', {
            'datos_sucursal': datos_sucursal,
            'datos_envio': request.POST,
            'Leatendio': usuario,
            'datos_usu': usuario,
            'numero_ticket': numero_ticket
        })

    return render(request, 'paqueteria/envio.html', {
        'datos_sucursal': datos_sucursal
    })


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

        if accion == 'regresar':
            return redirect('menu')

        numero_ticket = None

        if accion == 'guardar_imprimir':
            id_ticket = request.POST.get('id_ticket')
            with connection.cursor() as cursor:
                if id_ticket:
                    cursor.execute('''
                        UPDATE Devolucion
                        SET NombreCliente = %s,
                            FechaEntrega = %s,
                            HoraEntrega = %s
                        WHERE id = %s
                    ''', [nombre_cliente, fecha_entrega, hora_entrega, id_ticket])
                    numero_ticket = id_ticket
                else:
                    cursor.execute('CALL InsertarDevolucion(%s, %s, %s, %s)', 
                                   [nombre_cliente, fecha_entrega, hora_entrega, id_sucursal])

                    resultado = cursor.fetchone()
                    if resultado:
                        numero_ticket = resultado[0]

        return render(request, 'paqueteria/ticket_devolucion.html', {
            'nombre_cliente': nombre_cliente,
            'fecha_entrega': fecha_entrega,
            'hora_entrega': hora_entrega,
            'paqueteria': nombre_sucursal,
            'numero_ticket': numero_ticket
        })

    return render(request, 'paqueteria/devolucion.html')


def buscar_ticket(request):
    tipo = request.GET.get('tipo')
    ticket_id = request.GET.get('id_ticket')

    if not tipo or not ticket_id:
        return redirect('menu')

    if tipo == 'devolucion':
        with connection.cursor() as cursor:
            cursor.execute('SELECT id, NombreCliente, FechaEntrega, HoraEntrega FROM Devolucion WHERE id = %s', [ticket_id])
            row = cursor.fetchone()

            if row:
                columnas = [col[0] for col in cursor.description]
                datos = dict(zip(columnas, row))
                return render(request, 'paqueteria/devolucion.html', {'datos_devolucion': datos})
            else:
                return render(request, 'paqueteria/devolucion.html', {'error': 'No se encontró el ticket'})

    return redirect('menu')
