from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib import messages
from decimal import Decimal, InvalidOperation
import serial
import time
from django.db import transaction
from .models import Producto, Venta, ProductoVenta


def leer_bascula():
    puerto = '/dev/ttyUSB0'
    baudios = 9600
    try:
        with serial.Serial(puerto, baudios, timeout=1) as ser:
            ser.write(b'P')
            time.sleep(0.5)
            if ser.in_waiting:
                data = ser.readline().decode('utf-8').rstrip()
                peso_str = ''.join(filter(lambda x: x.isdigit() or x == '.', data))
                return peso_str
            else:
                return "0"
    except serial.SerialException:
        return "0"


def obtener_venta_abierta():
    venta_abierta = Venta.objects.filter(abierta=True, operador=1).first()
    if not venta_abierta:
        venta_abierta = Venta.objects.create(abierta=True, operador=1)
    return venta_abierta


def hello(request):
    venta_actual = obtener_venta_abierta()
    productos_venta = ProductoVenta.objects.filter(venta=venta_actual)
    context = {'productosventa': productos_venta, 'ventaactual': venta_actual}
    return render(request, 'cuestionariopart1.html', context)


def check(request):
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        
        # Validación de que el código solo contiene números
        if not codigo.isdigit():
            messages.error(request, 'El código debe contener solo números.')
            return redirect('hello')
        
        peso_str = leer_bascula()
        
        try:
            peso = Decimal(peso_str)
            if peso == 0:
                messages.error(request, 'El peso no puede ser 0, verifique la balanza.')
                return redirect('hello')
        except InvalidOperation:
            messages.error(request, 'Peso inválido.')
            return redirect('hello')

        # Validación de que el producto existe en la base de datos
        producto = Producto.objects.filter(codigo=codigo).first()
        if producto is None:
            messages.error(request, 'No existe un producto con el código proporcionado.')
            return redirect('hello')

        precio_final = (producto.precio * peso).quantize(Decimal('0.01'))

        venta = obtener_venta_abierta()
        ProductoVenta.objects.create(
            producto=producto,
            venta=venta,
            cantidad=peso,
            subtotal=precio_final
        )

        venta.total = (venta.total or Decimal('0.00')) + precio_final
        venta.save()

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
        with transaction.atomic():
            producto_venta = ProductoVenta.objects.get(id=producto_venta_id)
            venta = producto_venta.venta
            producto_venta.delete()
            venta.total = sum(pv.subtotal for pv in ProductoVenta.objects.filter(venta=venta))
            venta.save()
            messages.success(request, 'Producto eliminado correctamente.')
    except ProductoVenta.DoesNotExist:
        messages.error(request, 'El producto ya ha sido eliminado.')

    return redirect('hello')


def finalizar_venta(request):
    venta_actual = get_object_or_404(Venta, abierta=True, operador=1)
    if venta_actual.total == Decimal('0.00'):
        messages.info(request, 'La venta no se guardó porque el total es 0.')
    else:
        venta_actual.abierta = False
        venta_actual.save()
        messages.success(request, 'Venta finalizada correctamente.')

    return redirect('hello')
