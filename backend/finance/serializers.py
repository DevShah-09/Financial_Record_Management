from rest_framework import serializers
from .models import FinancialRecord

class FinancialRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialRecord
        fields = '__all__'
        read_only_fields = ['user']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be a positive number.")
        return value