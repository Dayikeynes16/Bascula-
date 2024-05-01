from django.db import models

class Venta(models.Model):
    
    operador = models.IntegerField(null=True, blank=True)
    total = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    abierta = models.BooleanField(default=False)
    finalizada = models.BooleanField(default=False)
    METODOS_DE_PAGO = [
        ('Tarjeta', 'Tarjeta'),
        ('Transferencia', 'Transferencia'),
        ('Efectivo', 'Efectivo'),
    ]
    metodo_de_pago = models.CharField(max_length=20, choices=METODOS_DE_PAGO, default='Efectivo')
    fecha = models.DateTimeField(null=True, blank=True)
    cliente = models.BigIntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'ventas'


class Producto(models.Model):
    codigo = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=255)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        managed = False
        db_table = 'productos'


class ProductoVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=8, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'producto_ventas'
