"""budget URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from api.views import dashboard, budget, add_money, test_chart, GraphBudgetHistory
from django.urls import path
import django.contrib.auth.views as login_view
urlpatterns = [
    path("admin/", admin.site.urls, name='admin'),
    path("budget/<str:budget_name>/", budget, name='budget'),
    path("add_money/", add_money, name='add_money'),
    path("", dashboard, name='dashboard'),
    path("login/",  login_view.LoginView.as_view(template_name="api/login.html"), name='login'),
    path("logout/", login_view.LogoutView.as_view(template_name="api/login.html"), name='logout'),
    path("test_chart/", test_chart, name='test_chart'),
    path("api/v1/graph/history", GraphBudgetHistory, name='graph_history'),

]
