from django.urls import path,include

import accounts
from . import views
urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('',views.about,name='about'),
    path('account/', include('accounts.urls')),
    path('add-transaction/', views.create_transaction, name='add_transaction'),
    path('budget/',views.budget , name='budget'),
    path('exp-transactions/',views.transaction_list, name='exp-transactions'),
    path('edit-goal/',views.edit_goal, name='edit-goal'),
    path('create-goal/',views.create_goal, name='create-goal'),
    path('delete-goal/',views.delete_goal, name='delete-goal'),
    path('edit-category/',views.edit_category, name='edit-category'),
    path('create-category/',views.create_category, name='create-category'),
    path('delete-category/',views.delete_category, name='delete-category'),
    path('create-expense/',views.create_expense, name='create-expense'),
    path('edit-expense/',views.edit_expense, name='edit-expense'),
    path('delete-expense/',views.delete_expense, name='delete-expense'),
    path('edit-income/',views.edit_income, name='edit-income'),
    path('edit-income/', views.edit_income, name='edit_income'),
     path(
      'transactions/<int:transaction_number>/delete/',
      views.delete_transaction,
      name='delete_transaction'
    ),
     path(
        'transactions/<int:transaction_number>/edit/',
        views.edit_transaction,
        name='edit_transaction'
    ),
]
