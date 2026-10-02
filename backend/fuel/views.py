from datetime import timedelta
from django.conf import settings
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.db.models import OuterRef, Subquery, Q
from django.middleware.csrf import get_token
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import serializers, viewsets, mixins
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .auth import AuthThrottle
from .models import Vehicle, Station, Refueling, PriceObservation, StationReport, FUEL_CHOICES, PAYMENT_CHOICES
from .serializers import VehicleSerializer, StationSerializer, RefuelingSerializer, ReportSerializer
User = get_user_model()
def session_data(request):
    u=request.user
    return {'user':{'id':u.pk,'name':u.first_name,'email':u.email} if u.is_authenticated else None,'csrfToken':get_token(request),'passwordResetAvailable':bool(settings.EMAIL_HOST)}
class SessionView(APIView):
    permission_classes=[AllowAny]
    def get(self,request): return Response(session_data(request))
class RegistrationInput(serializers.Serializer):
    name=serializers.CharField(max_length=150)
    email=serializers.EmailField(max_length=150)
    password=serializers.CharField(min_length=10,max_length=128,trim_whitespace=False)
class RegisterView(APIView):
    permission_classes=[AllowAny]
    throttle_classes=[AuthThrottle]
    def post(self,request):
        data=RegistrationInput(data=request.data); data.is_valid(raise_exception=True); d=data.validated_data
        email=d['email'].lower(); candidate=User(username=email,email=email,first_name=d['name'])
        try: validate_password(d['password'],candidate)
        except DjangoValidationError as exc: raise serializers.ValidationError({'password':exc.messages})
        try:
            with transaction.atomic(): candidate.set_password(d['password']); candidate.save()
        except IntegrityError: raise serializers.ValidationError({'email':'Não foi possível criar uma conta com este e-mail. Tente entrar ou recuperar a senha.'})
        login(request,candidate)
        return Response(session_data(request),status=201)
class LoginInput(serializers.Serializer):
    email=serializers.EmailField(max_length=150)
    password=serializers.CharField(max_length=128,trim_whitespace=False)
class LoginView(APIView):
    permission_classes=[AllowAny]
    throttle_classes=[AuthThrottle]
    def post(self,request):
        data=LoginInput(data=request.data); data.is_valid(raise_exception=True)
        user=authenticate(request,username=data.validated_data['email'].lower(),password=data.validated_data['password'])
        if user is None: return Response({'detail':'E-mail ou senha inválidos.'},status=400)
        login(request,user)
        return Response(session_data(request))
class LogoutView(APIView):
    def post(self,request): logout(request); return Response(session_data(request))
class PasswordResetView(APIView):
    permission_classes=[AllowAny]
    throttle_classes=[AuthThrottle]
    def post(self,request):
        email=serializers.EmailField(max_length=150).run_validation(request.data.get('email')).lower()
        if not settings.EMAIL_HOST: return Response({'detail':'Recuperação por e-mail ainda não configurada neste servidor.'},status=503)
        user=User.objects.filter(username=email,is_active=True).first()
        if user:
            uid=urlsafe_base64_encode(force_bytes(user.pk)); token=default_token_generator.make_token(user)
            url=f'{settings.PUBLIC_APP_URL}/?uid={uid}&token={token}'
            try: send_mail('Redefina sua senha — Meu Combustível',f'Você solicitou uma nova senha. Acesse o link em até 1 hora:\n\n{url}\n\nSe não foi você, ignore este e-mail.',settings.DEFAULT_FROM_EMAIL,[user.email])
            except Exception: return Response({'detail':'Não foi possível enviar o e-mail agora. Tente novamente mais tarde.'},status=503)
        return Response({'detail':'Se houver uma conta com esse e-mail, você receberá as instruções.'})
class PasswordConfirmView(APIView):
    permission_classes=[AllowAny]
    throttle_classes=[AuthThrottle]
    def post(self,request):
        try: user=User.objects.get(pk=force_str(urlsafe_base64_decode(str(request.data.get('uid','')))))
        except (ValueError,TypeError,OverflowError,User.DoesNotExist,UnicodeDecodeError): return Response({'detail':'Link inválido ou expirado.'},status=400)
        if not default_token_generator.check_token(user,str(request.data.get('token',''))): return Response({'detail':'Link inválido ou expirado.'},status=400)
        password=serializers.CharField(min_length=10,max_length=128,trim_whitespace=False).run_validation(request.data.get('password'))
        try: validate_password(password,user)
        except DjangoValidationError as exc: raise serializers.ValidationError({'password':exc.messages})
        user.set_password(password); user.save(update_fields=['password'])
        return Response({'detail':'Senha atualizada. Entre com a nova senha.'})
class VehicleViewSet(viewsets.ModelViewSet):
    serializer_class=VehicleSerializer
    def get_queryset(self): return Vehicle.objects.filter(owner=self.request.user)
    def perform_create(self,serializer): serializer.save(owner=self.request.user)
    def destroy(self,request,*args,**kwargs):
        vehicle=self.get_object()
        if vehicle.refuelings.exists(): return Response({'detail':'Este veículo possui abastecimentos. Preserve-o para manter seu histórico.'},status=409)
        with transaction.atomic():
            vehicle.delete(); first=Vehicle.objects.filter(owner=request.user).first()
            if first and not Vehicle.objects.filter(owner=request.user,primary=True).exists(): first.primary=True; first.save(update_fields=['primary'])
        return Response(status=204)
class StationViewSet(mixins.ListModelMixin,mixins.RetrieveModelMixin,mixins.CreateModelMixin,viewsets.GenericViewSet):
    serializer_class=StationSerializer
    def get_permissions(self): return [AllowAny()] if self.action in ('list','retrieve') else super().get_permissions()
    def get_queryset(self):
        fuel=self.request.query_params.get('fuel','Gasolina comum'); payment=self.request.query_params.get('payment','Pix')
        if fuel not in dict(FUEL_CHOICES) or payment not in dict(PAYMENT_CHOICES): raise serializers.ValidationError('Combustível ou condição de pagamento inválidos.')
        earliest=timezone.localdate()-timedelta(days=settings.PRICE_MAX_AGE_DAYS)
        latest=PriceObservation.objects.filter(station=OuterRef('pk'),fuel=fuel,payment=payment,date__gte=earliest,date__lte=timezone.localdate(),currency='BRL',unit='L').order_by('-date','-id')
        common_payment = self.request.query_params.get('common_payment', 'Pix')
        if common_payment not in ('Pix', 'Dinheiro', 'Débito'):
            raise serializers.ValidationError('Pagamento comum inválido.')
        prices = PriceObservation.objects.filter(station=OuterRef('pk'), fuel=fuel,
            date__gte=earliest, date__lte=timezone.localdate(), currency='BRL', unit='L').order_by('-date', '-id')
        common = prices.filter(payment=common_payment)
        credit = prices.filter(payment='Crédito')
        qs=Station.objects.annotate(price=Subquery(latest.values('price')[:1]),updated=Subquery(latest.values('date')[:1]),
            common_price=Subquery(common.values('price')[:1]), common_updated=Subquery(common.values('date')[:1]),
            credit_price=Subquery(credit.values('price')[:1]), credit_updated=Subquery(credit.values('date')[:1])).order_by('name')
        for field in ('city','state','country'):
            if self.request.query_params.get(field): qs=qs.filter(**{field+'__iexact':self.request.query_params[field]})
        if self.request.query_params.get('q'): qs=qs.filter(Q(name__icontains=self.request.query_params['q'])|Q(address__icontains=self.request.query_params['q']))
        return qs
    def create(self,request,*args,**kwargs):
        serializer=self.get_serializer(data=request.data); serializer.is_valid(raise_exception=True)
        data=dict(serializer.validated_data); data.setdefault('country','BR'); fingerprint=Station.make_fingerprint(data)
        external_id = data.get('external_id')
        if external_id:
            existing = Station.objects.filter(external_id=external_id).first()
            if existing:
                return Response(self.get_serializer(existing).data, status=200)
        try:
            with transaction.atomic():
                station,created=Station.objects.get_or_create(fingerprint=fingerprint,defaults={**data,'created_by':request.user,'air_confirmed_at':timezone.localdate() if data.get('air','Não informado')!='Não informado' else None})
                if not created and external_id and not station.external_id:
                    station.external_id = external_id
                    station.save(update_fields=['external_id'])
        except IntegrityError:
            station = Station.objects.filter(external_id=external_id).first() if external_id else None
            if station is None:
                raise
            created = False
        return Response(self.get_serializer(station).data,status=201 if created else 200)
class RefuelingViewSet(viewsets.ModelViewSet):
    serializer_class=RefuelingSerializer
    def get_queryset(self): return Refueling.objects.filter(owner=self.request.user).select_related('vehicle','station')
    def sync_price(self,obj):
        if not obj.share:
            PriceObservation.objects.filter(source=obj).delete()
            return
        prices = {obj.payment: obj.price}
        if obj.common_price is not None:
            prices[obj.common_payment] = obj.common_price
        if obj.credit_price is not None:
            prices['Crédito'] = obj.credit_price
        PriceObservation.objects.filter(source=obj).exclude(payment__in=prices).delete()
        for payment, price in prices.items():
            PriceObservation.objects.update_or_create(source=obj, payment=payment,
                defaults={'station':obj.station, 'fuel':obj.fuel, 'price':price, 'date':obj.date})
    def create(self,request,*args,**kwargs):
        serializer=self.get_serializer(data=request.data); serializer.is_valid(raise_exception=True)
        client_id=serializer.validated_data.get('client_id')
        if client_id:
            existing=self.get_queryset().filter(client_id=client_id).first()
            if existing: return Response(self.get_serializer(existing).data)
        try:
            with transaction.atomic(): obj=serializer.save(owner=request.user); self.sync_price(obj)
        except IntegrityError:
            if client_id:
                existing=self.get_queryset().filter(client_id=client_id).first()
                if existing: return Response(self.get_serializer(existing).data)
            raise
        return Response(self.get_serializer(obj).data,status=201)
    @transaction.atomic
    def perform_update(self,serializer): obj=serializer.save(); self.sync_price(obj)
class ReportViewSet(mixins.ListModelMixin,mixins.CreateModelMixin,viewsets.GenericViewSet):
    serializer_class=ReportSerializer
    def get_queryset(self): return StationReport.objects.filter(owner=self.request.user)
    def perform_create(self,serializer): serializer.save(owner=self.request.user,status='pending')
