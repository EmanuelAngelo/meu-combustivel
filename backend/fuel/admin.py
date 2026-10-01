from django.contrib import admin
from .models import Station, StationReport
@admin.register(StationReport)
class ReportAdmin(admin.ModelAdmin):
    list_display=('station','type','status','date')
    list_filter=('status','type')
    readonly_fields=('owner','created_at')
    actions=['approve','reject']
    @admin.action(description='Aprovar relatos selecionados (não comprova adulteração)')
    def approve(self,request,queryset): queryset.update(status='approved')
    @admin.action(description='Rejeitar relatos selecionados')
    def reject(self,request,queryset): queryset.update(status='rejected')
@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display=('name','city','state','air')
    search_fields=('name','address','city')
    readonly_fields=('fingerprint','created_by','created_at')
admin.site.site_header='Meu Combustível — Administração'
admin.site.site_title='Meu Combustível'
# Private vehicles and refuelings are not exposed in the admin interface.
