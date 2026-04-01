from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import FinancialRecord
from .serializers import FinancialRecordSerializer
from users.permissions import IsAdmin, IsAnalystOrAdmin
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum


class FinancialRecordViewSet(viewsets.ModelViewSet):
    queryset = FinancialRecord.objects.all()
    serializer_class = FinancialRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [IsAnalystOrAdmin()]

@api_view(['GET'])
def dashboard_summary(request):
    income = FinancialRecord.objects.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    expense = FinancialRecord.objects.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0

    return Response({
        "total_income": income,
        "total_expense": expense,
        "net_balance": income - expense
    })