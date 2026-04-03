from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FinancialRecordViewSet, dashboard_summary, category_summary, monthly_trends, recent_activity

router = DefaultRouter()
router.register('records', FinancialRecordViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', dashboard_summary),
    path('category-summary/', category_summary),
    path('monthly-trends/', monthly_trends),
    path('recent-activity/', recent_activity),
]