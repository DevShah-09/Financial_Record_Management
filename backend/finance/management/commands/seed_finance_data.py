import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import User
from finance.models import FinancialRecord

class Command(BaseCommand):
    help = 'Seed the database with initial users and financial data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')

        # Create Users
        users_data = [
            {'username': 'admin_user', 'email': 'admin@example.com', 'role': 'admin', 'password': 'Password123!', 'is_active': True},
            {'username': 'analyst_user', 'email': 'analyst@example.com', 'role': 'analyst', 'password': 'Password123!', 'is_active': True},
            {'username': 'viewer_user', 'email': 'viewer@example.com', 'role': 'viewer', 'password': 'Password123!', 'is_active': True},
        ]

        created_users = []
        for u_data in users_data:
            user, created = User.objects.get_or_create(
                username=u_data['username'],
                email=u_data['email'],
                defaults={'role': u_data['role'], 'is_active': u_data['is_active']}
            )
            if created:
                user.set_password(u_data['password'])
                user.save()
                self.stdout.write(self.style.SUCCESS(f"User {user.username} created"))
            else:
                self.stdout.write(f"User {user.username} already exists")
            created_users.append(user)

        # Create Financial Records
        categories = ['Salary', 'Groceries', 'Rent', 'Investments', 'Dining', 'Travel', 'Utilities']
        types = ['income', 'expense']

        for user in created_users:
            if FinancialRecord.objects.filter(user=user).exists():
                self.stdout.write(f"Records already exist for {user.username}, skipping...")
                continue

            for _ in range(10):
                amount = round(random.uniform(10.0, 5000.0), 2)
                t_type = random.choice(types)
                category = random.choice(categories)
                date = timezone.now().date() - timezone.timedelta(days=random.randint(0, 90))
                
                FinancialRecord.objects.create(
                    user=user,
                    amount=amount,
                    type=t_type,
                    category=category,
                    date=date,
                    notes=f"Auto-generated {t_type} for {user.username}"
                )
            self.stdout.write(self.style.SUCCESS(f"Created 10 records for {user.username}"))

        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully.'))
