from django.db import models
import datetime
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.db.models import Sum
import openai
import os

from openai import OpenAI


def get_unnamed_user():
    user, created = User.objects.get_or_create(
        username='unnamed',
        defaults={
            'email': 'unnamed@example.com',
            'password': '',  # Unusable password; can use User.set_unusable_password() later
            'last_login': now(),
            'date_joined': now(),
            'is_active': False,
            'is_staff': False,
            'is_superuser': False,
        }
    )
    return user.id
# Create your models here.
class Transaction(models.Model):
    # Sets up relationship between transaction and user; if user is deleted, so are their transacatins
    user = models.ForeignKey(User, on_delete=models.CASCADE,default = get_unnamed_user)
    #defines database to include category, name, amount, and date fields
    category = models.ForeignKey('Category', on_delete=models.CASCADE);
    name = models.CharField(max_length=150,default = 'unnamed')
    amount = models.DecimalField(max_digits = 10, decimal_places = 2)
    date = models.DateField()
    transaction_number = models.CharField(max_length = 20, blank = False) # shouldnt blank be false

    #saves the transaction number when transaction object is created.
    def save(self, *args, **kwargs):
        if not self.transaction_number:
            self.transaction_number = f"T{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        if not self.date:
            self.date = datetime.datetime.now()

        super().save(*args, **kwargs) #call parent class to save to the database
    def __str__(self):
        return f'category: {self.category} name: {self.name} amount: {self.amount} date: {self.date} transaction number: {self.transaction_number}  '

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=get_unnamed_user)
    name = models.CharField(max_length=150)
    budget = models.DecimalField(max_digits = 10, decimal_places = 2)
    @property
    def percentage(self):
        # Safely access the user's income
        income = self.user.income.first() if hasattr(self.user.income, 'all') else self.user.income
        total_income = income.amount if income else Decimal('1.00')  # Avoid division by zero

        total_expenses = self.user.expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        remaining_income = total_income - total_expenses

        if remaining_income == 0:
            return "0.00%"

        percent = (self.budget / remaining_income) * 100
        return f'{round(percent, 2)}%'
    @ property
    def spent(self):
        return sum(t.amount for t in self.transaction_set.all())
    def __str__(self):
        return f'name: {self.name} budget: {self.budget} spent: {self.spent}'
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=get_unnamed_user)
    goal = models.TextField()
    number = models.IntegerField()
    #creating an incrementing goal number for each goal
    def save(self, *args, **kwargs):
        # If it's a new goal, set the goal_number
        if self.number is None:
            last_goal = Goal.objects.filter(user=self.user).order_by('-number').first()
            if last_goal:
                self.number = last_goal.number + 1
            else:
                self.number = 1  # Start from 1 for the first goal
        super().save(*args, **kwargs)
    class Meta:
        verbose_name = "Goal"
        verbose_name_plural = "Goals"

class Exspenses(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=get_unnamed_user, related_name='expenses')
    expense = models.CharField(max_length = 150)
    amount = models.DecimalField(max_digits = 10, decimal_places = 2)
    class Meta:
        verbose_name = "Expense"
        verbose_name_plural = "Expenses"

class Income(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # ensures only one income per user
    amount = models.DecimalField(max_digits = 10, decimal_places = 2)
    class Meta:
        verbose_name = "Income"
        verbose_name_plural = "Income"
class OpenAIClient:
    _instance = None
    _api_key = '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'

    def __init__(self):
        # Set the API key in the OpenAI client
        openai.api_key = self._api_key

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = OpenAIClient()  # The instance is created with the API key already set
        return cls._instance

    @property
    def chat(self):
        # Delegate the chat functionality to the openai module
        return openai.chat

    def get_api_key(self):
        return self._api_key
