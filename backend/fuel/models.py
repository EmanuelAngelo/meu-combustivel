import hashlib
import unicodedata
from django.conf import settings
from django.db import models
from django.db.models import Q
FUEL_CHOICES = [(v, v) for v in ['Gasolina comum', 'Gasolina aditivada', 'Etanol', 'Diesel S10', 'Diesel S500']]
PAYMENT_CHOICES = [(v, v) for v in ['Pix', 'Dinheiro', 'Débito', 'Crédito', 'Aplicativo / desconto']]
AIR_CHOICES = [(v, v) for v in ['Gratuito', 'Pago', 'Não informado']]
def normalized(value):
    value = ''.join(c for c in unicodedata.normalize('NFKD', value) if not unicodedata.combining(c))
    return ' '.join(value.casefold().split())
class Vehicle(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vehicles')
    type = models.CharField(max_length=20, choices=[(v,v) for v in ['Moto','Carro','Van','Caminhonete','Caminhão','Outro']])
    brand = models.CharField(max_length=80)
    model = models.CharField(max_length=80)
    year = models.PositiveSmallIntegerField()
    capacity = models.DecimalField(max_digits=7, decimal_places=3)
    fuel = models.CharField(max_length=30, choices=FUEL_CHOICES + [('Flex','Flex')])
    primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-primary', 'id']
        constraints = [models.UniqueConstraint(fields=['owner'], condition=Q(primary=True), name='one_primary_vehicle_per_user'), models.CheckConstraint(condition=Q(capacity__gt=0), name='vehicle_positive_capacity')]
    def __str__(self): return f'{self.brand} {self.model}'
class Station(models.Model):
    name = models.CharField(max_length=120)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=60)
    country = models.CharField(max_length=2, default='BR')
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    lng = models.DecimalField(max_digits=10, decimal_places=6)
    air = models.CharField(max_length=20, choices=AIR_CHOICES, default='Não informado')
    air_confirmed_at = models.DateField(null=True, blank=True)
    fingerprint = models.CharField(max_length=64, unique=True, editable=False)
    external_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    @staticmethod
    def make_fingerprint(data):
        return hashlib.sha256('|'.join(normalized(str(data[k])) for k in ['name','address','city','state','country']).encode()).hexdigest()
    def save(self, *args, **kwargs):
        self.fingerprint = self.make_fingerprint({k:getattr(self,k) for k in ['name','address','city','state','country']})
        super().save(*args, **kwargs)
    def __str__(self): return self.name
class Refueling(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='refuelings')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name='refuelings')
    station = models.ForeignKey(Station, on_delete=models.PROTECT, related_name='refuelings')
    date = models.DateField()
    fuel = models.CharField(max_length=30, choices=FUEL_CHOICES)
    price = models.DecimalField(max_digits=9, decimal_places=3)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    liters = models.DecimalField(max_digits=9, decimal_places=3)
    km = models.PositiveIntegerField(null=True, blank=True)
    full = models.BooleanField(default=False)
    payment = models.CharField(max_length=30, choices=PAYMENT_CHOICES)
    note = models.TextField(max_length=1000, blank=True)
    share = models.BooleanField(default=True)
    acknowledged = models.BooleanField(default=False)
    common_payment = models.CharField(max_length=30, choices=[(v, v) for v in ['Pix', 'Dinheiro', 'Débito']], default='Pix')
    common_price = models.DecimalField(max_digits=9, decimal_places=3, null=True, blank=True)
    credit_price = models.DecimalField(max_digits=9, decimal_places=3, null=True, blank=True)
    client_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-date', '-id']
        constraints = [models.UniqueConstraint(fields=['owner','client_id'], name='unique_user_refueling_request'), models.CheckConstraint(condition=Q(price__gt=0)&Q(total__gt=0)&Q(liters__gt=0), name='positive_refueling_values')]
class PriceObservation(models.Model):
    source = models.ForeignKey(Refueling, on_delete=models.CASCADE, related_name='observations')
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='prices')
    fuel = models.CharField(max_length=30, choices=FUEL_CHOICES)
    price = models.DecimalField(max_digits=9, decimal_places=3)
    payment = models.CharField(max_length=30, choices=PAYMENT_CHOICES)
    currency = models.CharField(max_length=3, default='BRL')
    unit = models.CharField(max_length=10, default='L')
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['source', 'payment'], name='unique_source_payment')]
        indexes = [models.Index(fields=['station','fuel','payment','date'])]
class StationReport(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    type = models.CharField(max_length=50, choices=[(v,v) for v in ['Falhas após abastecer','Queda de rendimento','Dificuldade para ligar','Divergência nos valores','Calibrador indisponível','Outro problema']])
    description = models.TextField(max_length=1500)
    date = models.DateField()
    status = models.CharField(max_length=12, choices=[('pending','Pendente'),('approved','Aprovado'),('rejected','Rejeitado')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']
