from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from .models import Transaction, Category, Goal, Exspenses, Income
from decimal import Decimal
import datetime

class TransactionFactory:
    @staticmethod
    def create_transaction(user_id, category_id, name, amount, date=None):
        user = get_object_or_404(User, id=user_id)  # Get the actual User object
        category = get_object_or_404(Category, id=category_id, user=user)

        Transaction.objects.create(
            user=user,
            category=category,
            name=name,
            amount=amount,
            date=date,
        )
    @staticmethod
    def edit_transaction(user, transaction_number, category_id, name, amount, date=None):
        # Retrieve the transaction object for the user
        txn = get_object_or_404(Transaction, id=transaction_number, user=user)

        # Update the transaction fields
        txn.category = get_object_or_404(Category, id=category_id, user=user)
        txn.name = name
        txn.amount = Decimal(amount)
        if date:
            txn.date = date

        # Save the updated transaction to the database
        txn.save()

    @staticmethod
    def delete_transaction(user, transaction_number):
        # Logic to delete a transaction
        txn = get_object_or_404(Transaction, id=transaction_number, user=user)
        txn.delete()

class CategoryFactory:
        @staticmethod
        def create_category(user,name,budget):
            Category.objects.create(
                user=user,
                name=name,
                budget=budget,
            )
        @staticmethod
        def edit_category(user,current_name,new_name,new_budget):
            category = get_object_or_404(Category, name=current_name, user = user)
            category.name = new_name
            category.budget = new_budget
            category.save()

        @staticmethod
        def delete_category(user,category_name):
            category = get_object_or_404(Category, name=category_name, user=user)
            category.delete()

class GoalFactory:
    @staticmethod
    def create_goal(user,goal):
        Goal.objects.create(
            user=user,
            goal=goal,
        )
    @staticmethod
    def edit_goal(user, goal_number, new_goal):
        goal = get_object_or_404(Goal, number=goal_number, user=user)
        goal.goal = new_goal
        goal.save()

    @staticmethod
    def delete_goal(user, goal_number):
        goal = get_object_or_404(Goal, number=goal_number, user=user)
        goal.delete()

class ExpenseFactory:
    @staticmethod
    def create_expense(user,name,amount):
        Exspenses.objects.create(
            expense=name,
            amount=amount,
            user=user
        )


    @staticmethod
    def edit_expense(user, expense_name,new_expense,new_amount):
        expense = get_object_or_404(Exspenses, id=expense_name, user=user)
        expense.expense = new_expense
        expense.amount = new_amount
        expense.save()

    @staticmethod
    def delete_expense(user, expense_name):
        expense = get_object_or_404(Exspenses, expense=expense_name, user=user)
        expense.delete()

class IncomeFactory:
    @staticmethod
    def create_income(user,amount):
        Income.objects.create(
            user=user,
            amount=amount,
        )

    @staticmethod
    def edit_income(user,amount):
        income = get_object_or_404(Income, user=user)
        income.amount = amount
        income.save()
