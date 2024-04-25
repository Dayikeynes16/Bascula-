from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from Metricas.settings import os
from decimal import Decimal, InvalidOperation
import serial
import time
from django.contrib import messages
from .models import Producto, Venta, ProductoVenta


def leer_bascula():
    puerto = '/dev/tty.usbserial-1420' 
    baudios = 9600
    try:
        with serial.Serial(puerto, baudios, timeout=1) as ser:
            ser.write(b'P')
            time.sleep(0.5)
            if ser.in_waiting:
                data = ser.readline().decode('utf-8').rstrip()
                # Extraer solo la parte numérica
                peso_str = ''.join(filter(lambda x: x.isdigit() or x == '.', data))
                return peso_str
            else:
                return "0"  # Retorna "0" o algún valor por defecto si no hay respuesta
    except serial.SerialException as e:
        return "0"  # Retorna "0" o algún valor por defecto en caso de error


def obtener_venta_abierta():
    # Buscar una venta abierta con operador igual a 1
    venta_abierta = Venta.objects.filter(abierta=True, operador=1).first()

    # Si no existe una venta abierta con operador igual a 1, crear una nueva
    if not venta_abierta:
        venta_abierta = Venta.objects.create(abierta=True, operador=1)

    return venta_abierta


def hello(request):
   ventaactual = obtener_venta_abierta()
   productosventa = ProductoVenta.objects.filter(venta=ventaactual)
   context = {'productosventa': productosventa, 'ventaactual': ventaactual}
   return render(request, 'cuestionariopart1.html', context)



def check(request):
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        peso_str = leer_bascula()  # Llama a la función para obtener el peso

        try:
            peso = Decimal(peso_str)
        except InvalidOperation:
            return render(request, 'error.html', {'mensaje': 'Peso inválido'})
        if not Producto.objects.filter(codigo=codigo).exists():
            messages.error(request, 'No existe un producto con el código proporcionado.')
            return redirect('hello')

        producto = Producto.objects.get(codigo=codigo)
        producto = get_object_or_404(Producto, codigo=codigo)
        preciofinal = producto.precio * peso
        preciofinal = preciofinal.quantize(Decimal('0.001'))  # Redondear a 3 decimales

        # Verificar si existe una venta abierta
        venta = obtener_venta_abierta()
        # Crear un nuevo ProductoVenta y asociarlo con la venta encontrada o creada
        ProductoVenta.objects.create(
            producto=producto,
            venta=venta,
            cantidad=peso,
            subtotal=preciofinal
        )

        # Actualizar el total de la venta
        if venta.total is None:
            venta.total = Decimal('0.00')
        venta.total += preciofinal
        venta.save()

        # Actualizar el contexto para incluir la venta y el precio final
        context = {'peso': peso_str, 'codigo': codigo, 'preciofinal': preciofinal, 'producto': producto, 'venta': venta}

        return redirect('hello')
    return redirect('hello')

def agregar_producto(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        precio = request.POST.get('precio')

        Producto.objects.create(nombre=nombre, precio=precio)
        return redirect('agregar_producto')

    productos = Producto.objects.all()
    return render(request, 'product.html', {'productos': productos})


def eliminar_producto_venta(request, producto_venta_id):
    try:
        producto_venta = ProductoVenta.objects.get(id=producto_venta_id)
    except ProductoVenta.DoesNotExist:
        messages.warning(request, 'El producto ya ha sido eliminado.')
        return redirect('hello')

    venta_id = producto_venta.venta.id_venta
    producto_venta.delete()

    # Actualizar el total de la venta
    venta = get_object_or_404(Venta, id_venta=venta_id)
    venta.total = sum(item.subtotal for item in ProductoVenta.objects.filter(venta=venta))
    venta.save()

    return redirect('hello')


def finalizar_venta(request):
    
    ventaactual = get_object_or_404(Venta, abierta=True, operador=1)
    # Comprobar si el total de la venta es 0
    if ventaactual.total == Decimal('0.00'):
        # Aquí puedes decidir qué hacer si el total es 0. 
        # Por ejemplo, podrías eliminar la venta o simplemente redirigir a otra página.
        ventaactual.delete()
        messages.info(request, 'La venta no se guardó porque el total es 0.')
        return redirect('hello')

    ventaactual.abierta = False
    ventaactual.save()
    return redirect('hello')



        
        

