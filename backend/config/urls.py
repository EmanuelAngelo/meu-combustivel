from django.conf import settings
from django.contrib import admin
from django.http import FileResponse, JsonResponse
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from fuel.views import SessionView, RegisterView, LoginView, LogoutView, PasswordResetView, PasswordConfirmView, VehicleViewSet, StationViewSet, RefuelingViewSet, ReportViewSet
router=DefaultRouter()
router.register('vehicles',VehicleViewSet,basename='vehicle')
router.register('stations',StationViewSet,basename='station')
router.register('refuelings',RefuelingViewSet,basename='refueling')
router.register('reports',ReportViewSet,basename='report')
def frontend(request):
    if not settings.SERVE_FRONTEND:
        return JsonResponse({'service': 'Meu Combustível API', 'status': 'ok'})
    index=settings.FRONTEND_DIST/'index.html'
    if not index.exists(): return JsonResponse({'detail':'Compile o frontend com npm run build:server.'},status=503)
    response=FileResponse(index.open('rb'),content_type='text/html'); response['Cache-Control']='no-cache'; return response
urlpatterns=[path('admin/',admin.site.urls),path('api/auth/session/',SessionView.as_view()),path('api/auth/register/',RegisterView.as_view()),path('api/auth/login/',LoginView.as_view()),path('api/auth/logout/',LogoutView.as_view()),path('api/auth/password-reset/',PasswordResetView.as_view()),path('api/auth/password-confirm/',PasswordConfirmView.as_view()),path('api/',include(router.urls)),path('',frontend)]
