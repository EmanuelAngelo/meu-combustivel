import uuid
from pathlib import Path
from unittest import skipUnless
from decimal import Decimal
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient
from .models import Vehicle, Station, Refueling, PriceObservation
User=get_user_model()
@override_settings(SECURE_SSL_REDIRECT=False,SESSION_COOKIE_SECURE=False,CSRF_COOKIE_SECURE=False)
class APITests(TestCase):
    def setUp(self):
        cache.clear()
        self.a=User.objects.create_user(username='ana@example.com',email='ana@example.com',password='TestPassword123!')
        self.b=User.objects.create_user(username='bia@example.com',email='bia@example.com',password='TestPassword123!')
        self.car=Vehicle.objects.create(owner=self.a,type='Moto',brand='Yamaha',model='Fluo',year=2023,capacity='4.2',fuel='Gasolina comum',primary=True)
        self.other=Vehicle.objects.create(owner=self.b,type='Carro',brand='Fiat',model='Uno',year=2020,capacity='48',fuel='Gasolina comum',primary=True)
        self.station=Station.objects.create(name='Posto Teste',address='Rua A 12',city='São Luís',state='MA',lat='-2.5',lng='-44.2',created_by=self.a)
        self.client=APIClient(enforce_csrf_checks=True); self.client.force_login(self.a)
        self.client.credentials(HTTP_X_CSRFTOKEN=self.client.get('/api/auth/session/').json()['csrfToken'])
    def record(self,**updates):
        data={'vehicle':self.car.id,'station':self.station.id,'date':str(timezone.localdate()),'fuel':'Gasolina comum','price':'6.20','total':'23.04','liters':'3.716','payment':'Pix','client_id':str(uuid.uuid4())}; data.update(updates)
        return self.client.post('/api/refuelings/',data,format='json')
    def test_other_users_vehicle_is_inaccessible(self):
        self.assertEqual(len(self.client.get('/api/vehicles/').json()),1)
        for method in ('get','patch','delete'): self.assertEqual(getattr(self.client,method)(f'/api/vehicles/{self.other.pk}/',{'brand':'Hacked'},format='json').status_code,404)
        self.assertEqual(self.record(vehicle=self.other.pk).status_code,400)
    def test_private_refueling_list_detail_update_delete(self):
        r=self.record(); self.assertEqual(r.status_code,201,r.data); ident=r.data['id']
        self.client.force_login(self.b); self.client.credentials(HTTP_X_CSRFTOKEN=self.client.get('/api/auth/session/').json()['csrfToken'])
        self.assertEqual(self.client.get('/api/refuelings/').json(),[])
        for method in ('get','patch','delete'): self.assertEqual(getattr(self.client,method)(f'/api/refuelings/{ident}/',{'note':'x'},format='json').status_code,404)
    def test_precision_and_shared_projection(self):
        r=self.record(note='PRIVATE NOTE',km=1234)
        self.assertEqual(r.data['expected'],'23.04'); self.assertEqual(Decimal(r.data['difference']),0)
        item=APIClient().get('/api/stations/').json()[0]; self.assertEqual(item['price'],'6.200')
        for key in ('owner','vehicle','total','km','note','source'): self.assertNotIn(key,item)
        self.assertEqual(PriceObservation.objects.count(),1)
    def test_no_share_and_price_expiry(self):
        self.assertEqual(self.record(share=False).status_code,201); self.assertEqual(PriceObservation.objects.count(),0)
        self.record(date=str(timezone.localdate()-timedelta(days=8)))
        self.assertIsNone(self.client.get('/api/stations/').json()[0]['price'])
    def test_prices_are_separate_by_fuel_and_payment(self):
        self.record(fuel='Etanol',payment='Crédito')
        self.assertIsNone(self.client.get('/api/stations/').json()[0]['price'])
        self.assertEqual(self.client.get('/api/stations/?fuel=Etanol&payment=Crédito').json()[0]['price'],'6.200')
    def test_divergence_requires_review(self):
        self.assertEqual(self.record(total='25',expected='25').status_code,400)
        self.assertEqual(self.record(total='25',acknowledged=True).status_code,201)
        self.assertEqual(self.record(liters='7').status_code,400)
    def test_duplicate_retry_does_not_double_charge(self):
        ident=str(uuid.uuid4()); first=self.record(client_id=ident); second=self.record(client_id=ident)
        self.assertEqual(first.data['id'],second.data['id']); self.assertEqual(Refueling.objects.count(),1)
    def test_station_deduplication(self):
        data={'name':' Posto TESTE ','address':'Rua A 12','city':'Sao Luis','state':'MA','country':'BR','lat':'-2.5','lng':'-44.2','air':'Gratuito'}
        r=self.client.post('/api/stations/',data,format='json'); self.assertEqual(r.status_code,200,r.data); self.assertEqual(Station.objects.count(),1)
        self.assertEqual(self.client.patch(f'/api/stations/{self.station.id}/',{'name':'overwrite'},format='json').status_code,405)
    def test_report_cannot_self_approve(self):
        r=self.client.post('/api/reports/',{'station':self.station.pk,'type':'Falhas após abastecer','description':'Motor apresentou falhas após abastecer.','date':str(timezone.localdate()),'status':'approved','owner':self.b.pk},format='json')
        self.assertEqual(r.status_code,201,r.data); self.assertEqual(r.data['status'],'pending')
        self.client.force_login(self.b); self.assertEqual(self.client.get('/api/reports/').json(),[])
    def test_primary_vehicle_constraint(self):
        r=self.client.post('/api/vehicles/',{'type':'Carro','brand':'Fiat','model':'Argo','year':2025,'capacity':'48','fuel':'Flex','primary':True},format='json')
        self.assertEqual(r.status_code,201,r.data); self.assertEqual(Vehicle.objects.filter(owner=self.a,primary=True).count(),1)
        self.car.refresh_from_db(); self.assertFalse(self.car.primary)
    def test_login_requires_csrf_and_logout_revokes_session(self):
        anon=APIClient(enforce_csrf_checks=True)
        self.assertEqual(anon.post('/api/auth/login/',{'email':'ana@example.com','password':'TestPassword123!'},format='json').status_code,403)
        token=anon.get('/api/auth/session/').json()['csrfToken']; anon.credentials(HTTP_X_CSRFTOKEN=token)
        r=anon.post('/api/auth/login/',{'email':'ana@example.com','password':'TestPassword123!'},format='json'); self.assertEqual(r.status_code,200,r.data)
        anon.credentials(HTTP_X_CSRFTOKEN=r.data['csrfToken']); self.assertEqual(anon.get('/api/vehicles/').status_code,200)
        self.assertEqual(anon.post('/api/auth/logout/',{},format='json').status_code,200); self.assertEqual(anon.get('/api/vehicles/').status_code,403)
    def test_anonymous_and_no_store(self):
        for endpoint in ('vehicles','refuelings','reports'): self.assertEqual(APIClient().get(f'/api/{endpoint}/').status_code,403)
        self.assertIn('no-store',self.client.get('/api/refuelings/')['Cache-Control'])
    def test_registration_and_password_validation(self):
        anon=APIClient(enforce_csrf_checks=True); anon.credentials(HTTP_X_CSRFTOKEN=anon.get('/api/auth/session/').json()['csrfToken'])
        self.assertEqual(anon.post('/api/auth/register/',{'name':'Teste','email':'new@example.com','password':'1234567890'},format='json').status_code,400)
        r=anon.post('/api/auth/register/',{'name':'Teste','email':'New@Example.com','password':'ExcellentTestPassword42!'},format='json')
        self.assertEqual(r.status_code,201,r.data); self.assertEqual(r.data['user']['email'],'new@example.com'); self.assertEqual(anon.get('/api/vehicles/').json(),[])
    def test_future_date_and_invalid_volume(self):
        self.assertEqual(self.record(date=str(timezone.localdate()+timedelta(days=1))).status_code,400)
        self.assertEqual(self.record(liters='0').status_code,400); self.assertEqual(self.record(price='-1').status_code,400)
    def test_unsharing_removes_observation(self):
        r=self.record(); self.assertEqual(self.client.patch(f"/api/refuelings/{r.data['id']}/",{'share':False},format='json').status_code,200)
        self.assertEqual(PriceObservation.objects.count(),0)
    @override_settings(EMAIL_HOST='smtp.example.test',EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',PUBLIC_APP_URL='https://example.test')
    def test_password_reset_single_use_and_neutral_response(self):
        from django.core import mail
        from urllib.parse import urlparse,parse_qs
        anon=APIClient(enforce_csrf_checks=True)
        anon.credentials(HTTP_X_CSRFTOKEN=anon.get('/api/auth/session/').json()['csrfToken'])
        unknown=anon.post('/api/auth/password-reset/',{'email':'unknown@example.com'},format='json')
        known=anon.post('/api/auth/password-reset/',{'email':self.a.email},format='json')
        self.assertEqual(unknown.data,known.data)
        link=next(line for line in mail.outbox[0].body.splitlines() if line.startswith('https:'))
        query=parse_qs(urlparse(link).query)
        payload={'uid':query['uid'][0],'token':query['token'][0],'password':'AnotherStrongTestPassword42!'}
        self.assertEqual(anon.post('/api/auth/password-confirm/',payload,format='json').status_code,200)
        self.assertEqual(anon.post('/api/auth/password-confirm/',payload,format='json').status_code,400)
        self.a.refresh_from_db(); self.assertTrue(self.a.check_password(payload['password']))
    @skipUnless((Path(__file__).resolve().parents[2] / 'frontend' / 'dist' / 'index.html').exists(), 'Optional combined deployment requires npm run build')
    @override_settings(SERVE_FRONTEND=True, WHITENOISE_ROOT=str(Path(__file__).resolve().parents[2] / 'frontend' / 'dist'))
    def test_static_app_manifest_and_serviceworker_are_served(self):
        self.client = APIClient()  # Rebuild middleware under the combined-mode override.
        import json
        from pathlib import Path
        response=self.client.get('/')
        self.assertEqual(response.status_code,200)
        self.assertIn(b'<div id="app">',b''.join(response.streaming_content))
        for path in ('/manifest.webmanifest','/sw.js','/icon-192.png','/icon-512.png','/icon-maskable-512.png'):
            self.assertEqual(self.client.get(path).status_code,200,path)
        manifest=json.loads((Path(__file__).resolve().parents[2]/'frontend'/'dist'/'manifest.webmanifest').read_text())
        self.assertEqual(manifest['display'],'standalone')
