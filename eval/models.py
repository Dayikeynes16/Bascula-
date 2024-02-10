from django.db import models



# Create your models here.
class Producto(models.Model):
    codigo = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=25)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return self.nombre + " "

class Venta(models.Model):
    id_venta = models.AutoField(primary_key=True)
    fecha = models.DateTimeField(auto_now_add=True, null = True)
    operador = models.IntegerField(null=True)

    finalizada = models.BooleanField(default=False)
    total = models.DecimalField(max_digits=10, decimal_places=2, default = 0.00)
    abierta = models.BooleanField(default=True)
    METODOS_DE_PAGO = (('efectivo', 'Efectivo'),('tarjeta', 'Tarjeta'),
    ('transferencia', 'Transferencia')) 
    metodo_de_pago = models.CharField(max_length=15, choices=METODOS_DE_PAGO, default='efectivo', null=True )
    def __str__(self):
        return f"Venta #{self.id_venta}"
 
class ProductoVenta(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    def __str__(self):
        return f"{self.producto.nombre} ({self.cantidad})"

