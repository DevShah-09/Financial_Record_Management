from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Sum, Q, Case, When, DecimalField
from django.db.models.functions import TruncMonth
from django_filters.rest_framework import DjangoFilterBackend
from .models import FinancialRecord
from .serializers import FinancialRecordSerializer
from users.permissions import IsAdmin, IsAnalystOrAdmin, IsOwner, DenyAll
from .services import trigger_ai_insight

class FinancialRecordViewSet(viewsets.ModelViewSet):
    """
    ViewSet for financial records. 
    Strictly scopes data access to the owner, unless the requester is an Admin.
    """
    queryset = FinancialRecord.objects.all()
    serializer_class = FinancialRecordSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['type', 'category', 'date']
    search_fields = ['category', 'notes']

    def get_queryset(self):
        """
        Admins and Analysts can see all data. 
        Viewers and others only see their own (but Viewers are blocked from listing records entirely).
        """
        user = self.request.user
        if not user.is_authenticated:
            return FinancialRecord.objects.none()
        if user.role in ['admin', 'analyst']:
            return FinancialRecord.objects.all()
        return FinancialRecord.objects.filter(user=user)

    def get_permissions(self):
        """
        Apply role-based and ownership-based permissions.
        - Create/Modify: Restricted to Admins.
        - View (List/Retrieve): Restricted to Analyst, Admin, or Owner.
        - Viewers: Cannot access this ViewSet (handled via role check).
        """
        user = self.request.user
        if not user.is_authenticated:
            return [IsAuthenticated()]

        if user.role == 'viewer':
            return [DenyAll()]

        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdmin()]
        
        return [IsAuthenticated(), IsAnalystOrAdmin(), IsOwner()]

    def perform_create(self, serializer):
        """
        Ensure the record is always created for the logged-in user.
        """
        record = serializer.save(user=self.request.user)
        try:
            trigger_ai_insight({
                "amount": float(record.amount),
                "type": record.type,
                "category": record.category
            })
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"AI insight trigger failed: {e}")

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    """
    Returns a unified summary for the logged-in user only.
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
    Returns category-wise totals for the logged-in user only.
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
    Returns monthly trends for the logged-in user only.
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
    Returns recent transactions for the logged-in user only.
    """
    records = (
        FinancialRecord.objects
        .filter(user=request.user)
        .order_by('-date', '-created_at')[:10]
    )
    serializer = FinancialRecordSerializer(records, many=True)
    return Response(serializer.data)
