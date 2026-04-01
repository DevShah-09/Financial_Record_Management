from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FinancialRecordViewSet, dashboard_summary

router = DefaultRouter()
router.register('records', FinancialRecordViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', dashboard_summary),
]