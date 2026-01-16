from django.urls import path
from . import views
from Money_Parse import views as money_parse_views
from .views import add_expense_view, add_category_view, add_goal_view, add_income_view

urlpatterns = [
    path('signup/', views.signup_view, name='accounts.signup'),
    path('login/', views.login_view, name='accounts.login'),
    path('logout/', views.logout_view, name='accounts.logout'),
    path('account_initialization/',views.account_initialization_view,name='accounts.account_initialization'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path("add-expense/", add_expense_view, name="add_expense"),
    path("add-goal/",add_goal_view, name="add_goal"),
    path("add-category/", add_category_view, name="add_category"),
    path("add-income/", add_income_view, name = "add_income"),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('accounts/reset-password/', views.reset_password, name='reset_password'),


]
