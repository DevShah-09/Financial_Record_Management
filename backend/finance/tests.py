from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User
from finance.models import FinancialRecord

class FinancialRecordTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(username='admin', email='a@e.com', password='pw', role='admin')
        self.analyst = User.objects.create_user(username='analyst', email='an@e.com', password='pw', role='analyst')
        self.viewer = User.objects.create_user(username='viewer', email='v@e.com', password='pw', role='viewer')
        
    def test_amount_validation(self):
        """Test that negative amounts are rejected."""
        self.client.force_authenticate(user=self.admin)
        url = '/api/records/'
        data = {
            'amount': -100.00,
            'type': 'expense',
            'category': 'Rent',
            'date': '2023-01-01'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('amount', response.data)

    def test_viewer_access_denied(self):
        """Test that a viewer cannot access the records list."""
        self.client.force_authenticate(user=self.viewer)
        url = '/api/records/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_analyst_can_view_all(self):
        """Test that an analyst can view records they don't own."""
        # Admin creates a record
        FinancialRecord.objects.create(user=self.admin, amount=500.00, type='income', category='Salary', date='2023-01-01')
        
        self.client.force_authenticate(user=self.analyst)
        url = '/api/records/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should see the record even if they don't own it
        self.assertTrue(len(response.data['results']) > 0)
