from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from .models import Vehicle, Station, Refueling, StationReport, FUEL_CHOICES, PAYMENT_CHOICES
class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id','type','brand','model','year','capacity','fuel','primary']
        read_only_fields = ['id']
    def validate_year(self, value):
        if not 1900 <= value <= date.today().year + 1: raise serializers.ValidationError('Confira o ano do veículo.')
        return value
    def validate_capacity(self, value):
        if value <= 0: raise serializers.ValidationError('Informe uma capacidade maior que zero.')
        return value
    @transaction.atomic
    def create(self, data):
        if not Vehicle.objects.filter(owner=data['owner']).exists(): data['primary'] = True
        if data.get('primary'): Vehicle.objects.filter(owner=data['owner'], primary=True).update(primary=False)
        return super().create(data)
    @transaction.atomic
    def update(self, instance, data):
        if data.get('primary'): Vehicle.objects.filter(owner=instance.owner, primary=True).exclude(pk=instance.pk).update(primary=False)
        result = super().update(instance, data)
        if not Vehicle.objects.filter(owner=instance.owner, primary=True).exists():
            result.primary = True
            result.save(update_fields=['primary'])
        return result
class StationSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=9, decimal_places=3, read_only=True, default=None)
    updated = serializers.DateField(read_only=True, default=None)
    class Meta:
        model = Station
        fields = ['id','name','address','city','state','country','lat','lng','air','air_confirmed_at','price','updated']
        read_only_fields = ['id','air_confirmed_at']
    def validate_lat(self, value):
        if not -90 <= value <= 90: raise serializers.ValidationError('Latitude inválida.')
        return value
    def validate_lng(self, value):
        if not -180 <= value <= 180: raise serializers.ValidationError('Longitude inválida.')
        return value
    def validate_country(self, value):
        if value.upper() != 'BR': raise serializers.ValidationError('O cadastro nesta versão está disponível para o Brasil.')
        return value.upper()
class RefuelingSerializer(serializers.ModelSerializer):
    expected = serializers.SerializerMethodField()
    difference = serializers.SerializerMethodField()
    effective = serializers.SerializerMethodField()
    class Meta:
        model = Refueling
        fields = ['id','vehicle','station','date','fuel','price','total','liters','km','full','payment','note','share','acknowledged','client_id','expected','difference','effective']
        read_only_fields = ['id']
        validators = [] # Idempotency is handled in the view within owner scope.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = self.context['request'].user
        self.fields['vehicle'].queryset = Vehicle.objects.filter(owner=user)
    def get_expected(self, obj): return str((obj.price*obj.liters).quantize(Decimal('.01'), rounding=ROUND_HALF_UP))
    def get_difference(self, obj): return str(obj.total-Decimal(self.get_expected(obj)))
    def get_effective(self, obj): return str((obj.total/obj.liters).quantize(Decimal('.001'), rounding=ROUND_HALF_UP))
    def validate(self, data):
        values = {k:data.get(k, getattr(self.instance,k,None)) for k in ['price','total','liters','vehicle','date','acknowledged']}
        if values['date'] > timezone.localdate(): raise serializers.ValidationError({'date':'A data não pode estar no futuro.'})
        if any(values[k] <= 0 for k in ['price','total','liters']): raise serializers.ValidationError('Preço, total e litros devem ser maiores que zero.')
        expected = (values['price']*values['liters']).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
        if (abs(values['total']-expected)>Decimal('.01') or values['liters']>values['vehicle'].capacity) and not values['acknowledged']:
            raise serializers.ValidationError({'acknowledged':'Confira os valores e confirme a revisão.'})
        return data
class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = StationReport
        fields = ['id','station','type','description','date','status','created_at']
        read_only_fields = ['id','status','created_at']
    def validate_description(self, value):
        if len(value.strip()) < 15: raise serializers.ValidationError('Descreva o ocorrido em pelo menos 15 caracteres.')
        return value.strip()
    def validate_date(self, value):
        if value > timezone.localdate(): raise serializers.ValidationError('A data não pode estar no futuro.')
        return value
