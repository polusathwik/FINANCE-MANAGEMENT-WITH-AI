
from django.contrib.auth import login, logout,authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from Money_Parse.models import Exspenses,Category,Goal,Income
from .forms import CustomUserCreationForm, ForgotPasswordForm
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect, get_object_or_404
from .forms import SecurityQuestionsForm, ResetPasswordForm
from .models import SecurityQuestions
import random

from django.contrib.auth.models import User
from .forms import UserCreationForm, SecurityQuestionsForm
from Money_Parse.factories import TransactionFactory, CategoryFactory, GoalFactory, ExpenseFactory, IncomeFactory



def signup_view(request):
    if request.user.is_authenticated:
        logout(request)

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        security_form = SecurityQuestionsForm(request.POST)
        if form.is_valid() and security_form.is_valid():
            # Save the user from the custom user creation form
            user = form.save()

            # Create the security questions object, assign the user, then save
            security_questions = security_form.save(commit=False)
            security_questions.user = user
            security_questions.save()

            # Optionally initialize session variables, log in the user, etc.
            login(request, user)
            request.session['expenses'] = []
            request.session['goals'] = []
            request.session['categories'] = []

            return redirect('accounts.account_initialization')
    else:
        form = CustomUserCreationForm()
        security_form = SecurityQuestionsForm()

    return render(request, 'accounts/signup.html', {
        'form': form,
        'security_form': security_form,
    })

def account_initialization_view(request):
    if 'expenses' not in request.session:
        request.session['expenses'] = []
    if 'goals' not in request.session:
        request.session['goals'] = []
    if 'categories' not in request.session:
        request.session['categories'] = []

    income = getattr(request.user, 'income', None)
    expenses = request.session.get('expenses', [])
    goals = request.session.get('goals', [])
    categories = request.session.get('categories', [])

    total_expense_amount = sum(float(exp['amount']) for exp in expenses)

    if income is None or income.amount == 0:
        income_amount = 1  # Avoid division by zero
    else:
        income_amount = float(income.amount)

    # Calculate budget and remain
    budget = income_amount - total_expense_amount
    remain = income_amount - total_expense_amount

    total_category_amount = sum(float(category['amount']) for category in categories)
    remaining = budget - total_category_amount if budget is not None else 0

    if request.method == 'POST' and 'submit' in request.POST:
        user = request.user
        for expense_data in expenses:
            expense = expense_data['expense']
            amount = expense_data['amount']
            ExpenseFactory.create_expense(user, expense, amount)
        for goal_data in goals:
            goal = goal_data['goal']
            GoalFactory.create_goal(user,goal)
        for category_data in categories:
            name = category_data['category']
            budget = category_data['amount']
            CategoryFactory.create_category(user,name,budget)

        # Clear session after saving
        request.session['expenses'] = []
        request.session['goals'] = []
        request.session['categories'] = []

        return redirect('dashboard')

    return render(request, 'accounts/account_initialization.html', {
        'expenses': expenses,
        'goals': goals,
        'categories': categories,
        'income': income,
        'budget': budget,
        'remaining': remaining,
        'remain': remain,
    })


def login_view(request):
    if request.user.is_authenticated:
        logout(request)

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})
def logout_view(request):
        logout(request)
        return redirect('about')



@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        logout(request)
        return redirect('about')

def add_income_view(request):
    if request.method == 'POST':
        if hasattr(request.user, 'income'):
            # user already has income
            messages.error(request, 'You have already set your income.')
        else:
            amount = request.POST.get('amount')
            user = request.user
            IncomeFactory.create_income(user, amount)
            messages.success(request, 'Income added successfully!')
    return redirect('accounts.account_initialization')
def add_expense_view(request):
    if request.method == 'POST':
        expense_name = request.POST.get('expense')
        amount = request.POST.get('amount')

        # Store the expense in session temporarily
        expenses = request.session.get('expenses', [])
        expenses.append({'expense': expense_name, 'amount': amount})
        request.session['expenses'] = expenses
        request.session.modified = True  # Ensure the session is updated

    return redirect('accounts.account_initialization')

def add_category_view(request):
    if request.method == 'POST':
        category = request.POST.get('category')
        amount = request.POST.get('amount')

        # Store the category in session temporarily
        categories = request.session.get('categories', [])
        categories.append({'category': category, 'amount': amount})
        request.session['categories'] = categories
        request.session.modified = True  # Ensure the session is updated

    return redirect('accounts.account_initialization')

def add_goal_view(request):
    if request.method == 'POST':
        goal = request.POST.get('goal')

        # Store the goal in session temporarily
        goals = request.session.get('goals', [])
        goals.append({'goal': goal})
        request.session['goals'] = goals
        request.session.modified = True  # Ensure the session is updated

    return redirect('accounts.account_initialization')

def forgot_password(request):
    if request.method == 'POST':
        username = request.POST.get('user')
        if not username:
            # If username is missing, redirect to login
            username = request.session.get('username')
        if not username:
            # If username is missing, redirect to login
            return redirect('accounts.login')

        # Store the username in session
        request.session['username'] = username  # Save username to session

        form = SecurityQuestionsForm(request.POST)

        if form.is_valid():
            # Retrieve username from session
            username = request.session.get('username')
            # Retrieve the username from session
              # Replace with actual view name if needed
            answer_1 = form.cleaned_data['answer_1']
            answer_2 = form.cleaned_data['answer_2']
            print(answer_1, answer_2)

            try:
                user = User.objects.get(username=username)
                print(user.username)
                security = SecurityQuestions.objects.get(user=user)

                # Randomly select question 1 or 2
                question_number = random.choice([1, 2])
                request.session['question_number'] = question_number  # Store the selected question

                # Compare the user's answer with the correct answer
                correct_answer = security.answer_1 if question_number == 1 else security.answer_2
                user_answer = answer_1 if question_number == 1 else answer_2

                if user_answer.strip().lower() == correct_answer.strip().lower():
                    # Answer is correct, redirect to reset password
                    return redirect('reset_password')  # Ensure this view exists

                else:
                    # Incorrect answer
                    error = "Incorrect answer. Please try again."
                    return render(request, 'accounts/forgot_password.html', {
                        'form': form,
                        'error': error
                    })
            except (User.DoesNotExist, SecurityQuestions.DoesNotExist):
                form.add_error('answer_1', "Invalid username or security answers.")

    else:
        form = SecurityQuestionsForm()

    return render(request, 'accounts/forgot_password.html', {'form': form})

def reset_password(request):
    # Get the username from the session
    username = request.session.get('username')

    if not username:
        return redirect('forgot_password')  # If no username is in the session, redirect back to forgot password

    user = get_object_or_404(User, username=username)

    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            # Update the password for the user
            user.password = make_password(form.cleaned_data['new_password1'])
            user.save()
            messages.success(request, "Your password has been reset successfully.")
            return redirect('accounts.login')  # Redirect to login after successful password reset
    else:
        form = ResetPasswordForm()

    return render(request, 'accounts/reset_password.html', {'form': form})
