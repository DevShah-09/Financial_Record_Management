from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Sum, Q, Case, When, DecimalField
from django.db.models.functions import TruncMonth
from django_filters.rest_framework import DjangoFilterBackend
from .models import FinancialRecord
from .serializers import FinancialRecordSerializer
from users.permissions import IsAdmin, IsAnalystOrAdmin
from .services import trigger_ai_insight

class FinancialRecordViewSet(viewsets.ModelViewSet):
    queryset = FinancialRecord.objects.all()
    serializer_class = FinancialRecordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['type', 'category', 'date']
    search_fields = ['category', 'notes']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return FinancialRecord.objects.all()
        return FinancialRecord.objects.filter(user=user)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [IsAnalystOrAdmin()]

    def perform_create(self, serializer):
        record = serializer.save(user=self.request.user)
        # Attempt AI trigger safely
        try:
            trigger_ai_insight({
                "amount": float(record.amount),
                "type": record.type,
                "category": record.category
            })
        except Exception as e:
            # For now, just logging; in production, use a proper error tracking system
            import logging
            logging.getLogger(__name__).error(f"AI insight trigger failed: {e}")

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    """
    Returns a unified summary of income, expense, and net balance for the user.
    Optimized for performance with a single conditional aggregation query.
    """
    summary = FinancialRecord.objects.filter(user=request.user).aggregate(
        total_income=Sum(
            Case(When(type='income', then='amount'), default=0, output_field=DecimalField())
        ),
        total_expense=Sum(
            Case(When(type='expense', then='amount'), default=0, output_field=DecimalField())
        )
    )

    income = summary['total_income'] or 0
    expense = summary['total_expense'] or 0

    return Response({
        "total_income": float(income),
        "total_expense": float(expense),
        "net_balance": float(income - expense)
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def category_summary(request):
    """
    Returns category-wise totals for the logged-in user.
    """
    data = (
        FinancialRecord.objects
        .filter(user=request.user)
        .values('category')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def monthly_trends(request):
    """
    Returns monthly income vs expense trends for the logged-in user.
    """
    data = (
        FinancialRecord.objects
        .filter(user=request.user)
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(
            income=Sum(Case(When(type='income', then='amount'), default=0, output_field=DecimalField())),
            expense=Sum(Case(When(type='expense', then='amount'), default=0, output_field=DecimalField()))
        )
        .order_by('month')
    )
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recent_activity(request):
    """
    Returns the most recent 10 transactions for the dashboard.
    """
    records = (
        FinancialRecord.objects
        .filter(user=request.user)
        .order_by('-date', '-created_at')[:10]
    )
    serializer = FinancialRecordSerializer(records, many=True)
    return Response(serializer.data)
