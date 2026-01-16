import openai
  # Ensure you import openai for API calls
from django.db.models import Sum, Q
from openai import OpenAI
import json
from .models import Transaction, Category, Exspenses, Goal, Income, OpenAIClient  # Corrected 'Exspenses' to 'Expenses'
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from decimal import Decimal
import os  # For loading the environment variable
from django.views.decorators.http import require_http_methods
from .factories import TransactionFactory, CategoryFactory, GoalFactory, ExpenseFactory, IncomeFactory
# Views for each corresponding Page of the app
def about(request):
    request.user = None
    return render(request, 'about.html',{}) #brackets at the end allow us to pass in stuff during render
@login_required
def budget(request):
    user = request.user
    categories = Category.objects.filter(user=user)
    goals = Goal.objects.filter(user=user)
    expenses = Exspenses.objects.filter(user=user)
    # Fix the typo from Exspenses to Expenses

    # Fetch the user's income (assuming each user has one income)
    income = Income.objects.filter(user=user).first()  # Use `.first()` to get the first income object
    total_expense_amount = sum(float(exp.amount) for exp in expenses)  # Ensure correct access to amount

    budget = None
    if income:
        budget = float(income.amount) - total_expense_amount  # Calculate budget if income exists
    # Ensure income exists and is valid
    if income is None or income.amount == 0:
        # If no income or income is 0, handle it as needed (e.g., set to 0 or skip)
        income_amount = 1  # Avoid division by zero, default to 1
    else:
        income_amount = float(income.amount)  # Convert income to float

    total_category_amount = sum(float(category.budget) for category in categories)

    remain = income_amount  - total_expense_amount
    # Calculate the remaining budget
    remaining = budget - total_category_amount if budget is not None else 0

    # Formatting the data for Google Charts API
    chart_data = [['Category', 'Amount']]

    for expense in expenses:
        expense_percentage = (float(expense.amount) / income_amount) * 100 if income_amount != 0 else 0  # Ensure division by float
        chart_data.append([expense.expense, expense.amount])

    # Serialize chart_data with custom decimal serializer
    chart_data_json = json.dumps(chart_data, default=decimal_default)

    return render(request, 'Budget.html', {
        'categories': categories,
        'goals': goals,
        'chart_data': chart_data_json,
        'income': income,
        'budget': budget,
        'remaining': remaining,
        'remain': remain,
        'expenses': expenses,
        'total_expense_amount': total_expense_amount,
    })

@login_required
def dashboard(request):
    user = request.user
    categories = Category.objects.filter(user = user)
    transactions = Transaction.objects.filter(user=user).order_by('-date', '-id')
    financial_advice = get_financial_suggestions(request.user)
    financial_advice_list = [line for line in financial_advice.split('\n') if line.strip()] if financial_advice else []

    category_data = []
    for cat in categories:
        percent = float((cat.spent / cat.budget) * 100) if cat.budget > 0 else 0
        category_data.append({
            'name': cat.name,
            'budget': cat.budget,
            'spent': cat.spent,
            'percent': percent,
        })

    return render(request, 'dashboard.html', {
        'categories': categories,
        'transactions': transactions,
        'category_data': category_data,
        'financial_advice': financial_advice_list,
    })
@login_required
def transaction_list(request):
    # Start with all this user's transactions, newest first
    txns = Transaction.objects.filter(user=request.user)

    # Get filter values from the GET request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    query = request.GET.get('q')
    alpha_order = request.GET.get('alpha_order')
    sort_by = request.GET.get('sort_by')

    # Apply start and end date filtering
    if start_date:
        txns = txns.filter(date__gte=start_date)
    if end_date:
        txns = txns.filter(date__lte=end_date)

    # Apply text search on the transaction name or description
    if query:
        txns = txns.filter(
            Q(name__icontains=query) |
            Q(category__name__icontains=query)
        )

    # Apply sorting by amount (smallest to largest or largest to smallest)
    if alpha_order == 'asc':
        txns = txns.order_by('amount')  # Sort by amount in ascending order
    elif alpha_order == 'desc':
        txns = txns.order_by('-amount')  # Sort by amount in descending order

    # Apply sorting by date or amount if no alpha_order is given
    if not alpha_order:  # Only apply this if no alphabetical order was set
        if sort_by == 'date':
            txns = txns.order_by('-date')
        elif sort_by == 'amount':
            txns = txns.order_by('-amount')

    return render(request, 'transaction_list.html', {
        'transactions': txns,
    })


@login_required
def create_transaction(request):
    if request.method == "POST":
        user_id = request.user.id  # Access the user ID directly
        category_id = request.POST['category']
        name = request.POST['name']
        amount = request.POST['amount']
        date = request.POST.get('date', None)

        # Use the factory method to create the transaction
        TransactionFactory.create_transaction(user_id, category_id, name, amount, date)

    return redirect('dashboard')

# Methods for editing, deleting and adding Transactions, Expenses, Income, and Categories, Goals etc.
@require_http_methods(["GET", "POST"])
def edit_transaction(request, transaction_number):
    if request.method == "POST":
        user = request.user
        transaction_number = transaction_number
        category_id = request.POST['category']
        name = request.POST['name']
        amount = request.POST['amount']
        date = request.POST.get('date', None)
        # Use the factory method to update the transaction
        TransactionFactory.edit_transaction( user,transaction_number,category_id,name,amount,date)
        return redirect('exp-transactions')   # or 'dashboard'

    # GET → Render form for editing
    txn = get_object_or_404(Transaction, id=transaction_number, user=request.user)
    return render(request, 'transaction_form.html', {
        'txn': txn,
        'categories': Category.objects.filter(user=request.user),
    })


def delete_transaction(request, transaction_number):
    if request.method == "POST":
        user = request.user
        transaction_number = transaction_number
        # Use the factory method to delete the transaction
        TransactionFactory.delete_transaction(user, transaction_number)
        return redirect('exp-transactions')  # or 'dashboard'
# methods for category database modification
def create_category(request):
    if request.method == "POST":
        user = request.user
        name = request.POST.get('new_category')
        budget = request.POST.get('new_budget')

        CategoryFactory.create_category(user,name, budget)
        return redirect('budget')

def edit_category(request):
    if request.method == "POST":
        current_name = request.POST.get('category')
        new_name = request.POST.get('new_category')
        new_budget = request.POST.get('new_budget')
        user = request.user

        CategoryFactory.edit_category(user, current_name, new_name, new_budget)
        return redirect('budget')
def delete_category(request):
    if request.method == "POST":
        category_name = request.POST.get('category')
        user = request.user

        CategoryFactory.delete_category(user, category_name)
        return redirect('budget')

# methods for Goal database modification
def create_goal(request):
    if request.method == "POST":
        user = request.user
        goal = request.POST.get('new_goal')

        GoalFactory.create_goal(user,goal)
        return redirect('budget')
def edit_goal(request):
    if request.method == "POST":
        goal_number = request.POST.get('goal_number')
        user = request.user
        new_goal = request.POST.get('new_goal')

        GoalFactory.edit_goal(user, goal_number, new_goal)
        return redirect('budget')
def delete_goal(request):
    if request.method == "POST":
        goal_number = request.POST.get('goal_number')
        user = request.user

        GoalFactory.delete_goal(user, goal_number)
    # renumbering goals after deletion made
    remaining_goals = Goal.objects.filter(user=request.user).order_by('number')
    for idx, goal in enumerate(remaining_goals, start=1):
        goal.number = idx
        goal.save()
    return redirect('budget')


# methods for exspense database modification
def create_expense(request):
    if request.method == "POST":
        user = request.user
        name = request.POST.get("new_expense")
        amount = request.POST.get("new_amount")

        ExpenseFactory.create_expense(user,name,amount)
        return redirect("budget")
def edit_expense(request):
    if request.method == "POST":
        expense_name = request.POST.get('expense')
        user = request.user
        new_expense = request.POST.get('new_expense')
        new_amount = request.POST.get('new_amount')

        ExpenseFactory.edit_expense(user, expense_name, new_expense, new_amount)
        return redirect('budget')
def delete_expense(request):
    if  request.method == "POST":
        expense_name = request.POST.get('expense')
        user = request.user

        ExpenseFactory.delete_expense(user, expense_name)
        return redirect('budget')

# methods for income database modification
def edit_income(request):
    if request.method == "POST":

        user = request.user
        new_income = request.POST.get('new_income')
        IncomeFactory.edit_income(user,new_income)

        return redirect('budget')
# additional helper methods
def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)  # or return str(obj) if you prefer to serialize as a string
    raise TypeError("Type not serializable")
client = OpenAI(api_key= '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')
          # Reset the API key if an error occurs
def get_financial_suggestions(user):
    # First, ensure the OpenAIClient is initialized
    openai_client = OpenAIClient.get_instance()  # This automatically sets the API key

    # Collect relevant user data
    income = Income.objects.filter(user=user).first()
    expenses = Exspenses.objects.filter(user=user)
    expenses_data = {expense.expense: expense.amount for expense in expenses}
    transactions = Transaction.objects.filter(user=user).order_by('-date', '-id')
    transactions_data = [
        {
            'id': transaction.id,
            'amount': transaction.amount,
            'date': transaction.date,
            'name': transaction.name,
            'category': transaction.category
        }
        for transaction in transactions
    ]
    categories = Category.objects.filter(user=user)
    categories_data = {category.name: category.budget for category in categories}

    # Create a prompt based on user data
    prompt = f"Provide 3 bullet points of financial advice specific to my transactions, expenses, income, categories provided in the following data:\nIncome: {income}\nExpenses: {expenses}\nCategories: {categories_data} \nExpenses: {expenses_data} \nTransaction: {transactions_data} (ensure there is not gaps between each point)"

    try:
        # Call the OpenAI API with the prompt using the singleton instance
        response = openai_client.chat.completions.create(  # This uses the OpenAI API
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a financial assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )

        advice = response.choices[0].message.content.strip()
        return advice
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return None


