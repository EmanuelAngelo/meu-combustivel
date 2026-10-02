from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from . import tests as fixtures
from django.test import TestCase, override_settings
from .models import Station, PriceObservation

# Reuse only the setup/helpers, without running the original suite twice.
@override_settings(SECURE_SSL_REDIRECT=False,SESSION_COOKIE_SECURE=False,CSRF_COOKIE_SECURE=False)
class PriceComparisonTests(TestCase):
    setUp = fixtures.APITests.setUp
    record = fixtures.APITests.record
    def test_common_and_credit_are_independent(self):
        response = self.record(common_price='6.200', credit_price='6.499')
        self.assertEqual(response.status_code, 201, response.data)
        station = self.client.get('/api/stations/').json()[0]
        self.assertEqual(station['common_price'], '6.200')
        self.assertEqual(station['credit_price'], '6.499')
        self.assertEqual(PriceObservation.objects.count(), 2)
        credit = self.client.get('/api/stations/?payment=Crédito').json()[0]
        self.assertEqual(credit['price'], '6.499')
        debit = self.client.get('/api/stations/?common_payment=Débito').json()[0]
        self.assertIsNone(debit['common_price'])

    def test_equal_credit_is_known_and_missing_credit_is_unknown(self):
        self.record(credit_price='6.200')
        station = self.client.get('/api/stations/').json()[0]
        self.assertEqual(station['credit_price'], station['common_price'])
        self.assertEqual(self.client.get('/api/stations/?fuel=Etanol').json()[0]['credit_price'], None)

    def test_comparison_expiry_and_private_prices(self):
        self.record(common_price='6.200', credit_price='6.499', share=False)
        self.assertEqual(PriceObservation.objects.count(), 0)
        self.record(credit_price='6.499', date=str(timezone.localdate()-timedelta(days=8)))
        station = self.client.get('/api/stations/').json()[0]
        self.assertIsNone(station['credit_price'])
        self.assertIsNone(station['common_price'])

    def test_conflicting_or_nonpositive_prices_rejected(self):
        for update in ({'common_price':'6.100'}, {'credit_price':'0'}, {'common_price':'-1'}, {'common_payment':'Crédito'}):
            self.assertEqual(self.record(**update).status_code, 400)

    def test_update_and_unshare_remove_obsolete_prices(self):
        response = self.record(credit_price='6.499')
        url = f"/api/refuelings/{response.data['id']}/"
        self.assertEqual(self.client.patch(url, {'credit_price':None}, format='json').status_code, 200)
        self.assertEqual(PriceObservation.objects.count(), 1)
        self.assertEqual(self.client.patch(url, {'share':False}, format='json').status_code, 200)
        self.assertEqual(PriceObservation.objects.count(), 0)

    def test_place_id_deduplicates_different_names(self):
        data = {'name':'Posto Maps','address':'Rua B','city':'São Luís','state':'MA','lat':'-2.5','lng':'-44.2','external_id':'place-test-123'}
        first = self.client.post('/api/stations/',data,format='json')
        self.assertEqual(first.status_code,201,first.data)
        data['name'] = 'Outro nome para o mesmo posto'
        second = self.client.post('/api/stations/',data,format='json')
        self.assertEqual(second.status_code,200,second.data)
        self.assertEqual(first.data['id'], second.data['id'])
        self.assertEqual(Station.objects.filter(external_id='place-test-123').count(), 1)
