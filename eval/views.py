from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from Metricas.settings import os
from decimal import Decimal, InvalidOperation
import serial
import time
from django.contrib import messages
from .models import Producto, Venta, ProductoVenta
from django.db import transaction
from django.http import Http404



def leer_bascula():
    puerto = 'COM4'
    baudios = 9600
    try:
        with serial.Serial(puerto, baudios, timeout=1) as ser:
            ser.write(b'P')
            time.sleep(0.5)
            if ser.in_waiting:
                data = ser.readline().decode('utf-8').rstrip()
                # Extraer solo la parte numérica
                peso_str = ''.join(filter(lambda x: x.isdigit() or x == '.', data))
                print('el resultado es'+ peso_str)
                return peso_str
            else:
                return "0"  # Retorna "0" o algún valor por defecto si no hay respuesta
    except serial.SerialException as e:
        return "0"  # Retorna "0" o algún valor por defecto en caso de error



def obtener_venta_abierta():
    venta_abierta = Venta.objects.filter(abierta=True, operador=2, finalizada = False).get()


    if not venta_abierta:
        venta_abierta = Venta.objects.create(abierta=True, operador=2,finalizada = False)

    return venta_abierta


def hello(request):
   ventaactual = obtener_venta_abierta()
   productosventa = ProductoVenta.objects.filter(venta=ventaactual)
   context = {'productosventa': productosventa, 'ventaactual': ventaactual}
   return render(request, 'cuestionariopart1.html', context)



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Producto, Venta, ProductoVenta
from decimal import Decimal, InvalidOperation

def check(request):
    special_codes = {
        '99': ('11', Decimal('0.5')),
        '98': ('12', Decimal('1.0')),
        # Add more special codes as needed
    }

    codigo = request.POST.get('codigo')
    if codigo in special_codes:
        codigo, peso = special_codes[codigo]  # Fetch the mapped code and weight
        peso_str = str(peso)  # Convert Decimal back to string for consistent context handling
    else:
        peso_str = leer_bascula()
        try:
            peso = Decimal(peso_str)
        except InvalidOperation:
            return render(request, 'error.html', {'mensaje': 'Peso inválido'})

    try:
        producto = get_object_or_404(Producto, codigo=codigo)
    except Http404:
        messages.error(request, 'No existe un producto con el código proporcionado.')
        return redirect('hello')
    preciofinal = (producto.precio * peso).quantize(Decimal('0.01'))

    with transaction.atomic():
        venta = obtener_venta_abierta()
        ProductoVenta.objects.create(
            producto=producto,
            venta=venta,
            cantidad=peso,
            subtotal=preciofinal
        )
        
        venta.total = (venta.total or Decimal('0.00')) + preciofinal
        venta.save()

    context = {
        'peso': peso_str,  # Now consistent across all cases
        'codigo': codigo,
        'preciofinal': preciofinal,
        'producto': producto,
        'venta': venta
    }

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
        with transaction.atomic():
            producto_venta = ProductoVenta.objects.get(id=producto_venta_id)
            venta = producto_venta.venta
            producto_venta.delete()

            # Recalcular el total después de eliminar el producto
            venta.total = sum(pv.subtotal for pv in ProductoVenta.objects.filter(venta=venta))
            venta.save()
            messages.success(request, 'Producto eliminado correctamente.')
    except ProductoVenta.DoesNotExist:
        # Este mensaje se mostrará si se intenta acceder a un ProductoVenta ya eliminado
        messages.error(request, 'El producto ya ha sido eliminado.')

    return redirect('hello')

def finalizar_venta(request):
    venta_actual = get_object_or_404(Venta, abierta=True, operador=2, finalizada = False)
    if venta_actual.total == Decimal('0.00'):
        messages.info(request, 'La venta no se guardó porque el total es 0.')
    else:
        venta_actual.abierta = False

        venta_actual.save()
        messages.success(request, 'Venta finalizada correctamente.')
    return redirect('hello')


        
        
