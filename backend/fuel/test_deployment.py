from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

FRONTEND = 'https://meu-combustivel.example.test'

@override_settings(
    ALLOWED_HOSTS=['testserver'],
    CORS_ALLOWED_ORIGINS=[FRONTEND],
    CSRF_TRUSTED_ORIGINS=[FRONTEND],
    SESSION_COOKIE_SECURE=True,
    CSRF_COOKIE_SECURE=True,
    SECURE_SSL_REDIRECT=True,
)
class DeploymentTests(TestCase):
    def setUp(self):
        cache.clear()
        get_user_model().objects.create_user(username='deploy@example.test', password='TestDeployment42!')
        self.client = APIClient(enforce_csrf_checks=True)

    def test_allowed_preflight_with_csrf_header(self):
        response = self.client.options('/api/auth/login/', secure=True,
            HTTP_ORIGIN=FRONTEND, HTTP_ACCESS_CONTROL_REQUEST_METHOD='POST',
            HTTP_ACCESS_CONTROL_REQUEST_HEADERS='content-type,x-csrftoken')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Access-Control-Allow-Origin'], FRONTEND)
        self.assertEqual(response['Access-Control-Allow-Credentials'], 'true')
        self.assertIn('x-csrftoken', response['Access-Control-Allow-Headers'])

    def test_unlisted_origin_does_not_receive_cors_permission(self):
        response = self.client.options('/api/auth/login/', secure=True,
            HTTP_ORIGIN='https://other-project.vercel.app', HTTP_ACCESS_CONTROL_REQUEST_METHOD='POST')
        self.assertNotIn('Access-Control-Allow-Origin', response)

    def test_session_rotation_logout_and_cache_through_trusted_origin(self):
        response = self.client.get('/api/auth/session/', secure=True, HTTP_ORIGIN=FRONTEND)
        self.assertIn('no-store', response['Cache-Control'])
        self.assertEqual(response['Access-Control-Allow-Origin'], FRONTEND)
        token = response.json()['csrfToken']
        response = self.client.post('/api/auth/login/',
            {'email':'deploy@example.test', 'password':'TestDeployment42!'}, format='json',
            secure=True, HTTP_ORIGIN=FRONTEND, HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 200, response.data)
        for name in ('sessionid', 'csrftoken'):
            self.assertTrue(response.cookies[name]['secure'])
            self.assertTrue(response.cookies[name]['httponly'])
            self.assertEqual(response.cookies[name]['samesite'], 'Lax')
            self.assertEqual(response.cookies[name]['domain'], '')
        new_token = response.json()['csrfToken']
        self.assertNotEqual(token, new_token)
        self.assertEqual(self.client.get('/api/vehicles/', secure=True).status_code, 200)
        response = self.client.post('/api/auth/logout/', {}, format='json', secure=True,
            HTTP_ORIGIN=FRONTEND, HTTP_X_CSRFTOKEN=new_token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get('/api/vehicles/', secure=True).status_code, 403)

    def test_trusted_origin_still_requires_csrf(self):
        response = self.client.post('/api/auth/login/', {}, format='json', secure=True, HTTP_ORIGIN=FRONTEND)
        self.assertEqual(response.status_code, 403)

    def test_valid_token_does_not_allow_untrusted_origin(self):
        token = self.client.get('/api/auth/session/', secure=True).json()['csrfToken']
        response = self.client.post('/api/auth/login/', {}, format='json', secure=True,
            HTTP_X_CSRFTOKEN=token, HTTP_ORIGIN='https://evil.example.test')
        self.assertEqual(response.status_code, 403)
        self.assertNotIn('Access-Control-Allow-Origin', response)

    @override_settings(SERVE_FRONTEND=False)
    def test_backend_does_not_require_frontend_build(self):
        response = self.client.get('/', secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['service'], 'Meu Combustível API')
        self.assertEqual(self.client.get('/api/does-not-exist/', secure=True).status_code, 404)

    def test_admin_does_not_expose_cors(self):
        response = self.client.get('/admin/login/', secure=True, HTTP_ORIGIN=FRONTEND)
        self.assertNotIn('Access-Control-Allow-Origin', response)
