"""
URL configuration for dashboard project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
# from django.contrib import admin
# from django.urls import path, include
# from . import views

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', views.project_index, name = "homepage"),
#     path("<int:pk>/", views.project_detail, name = "project_detail"),
#     path('dashboard/', views.dashboard, name = "dashboard")
# ]

from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.views import serve
from .views import *
from django.views.generic import TemplateView
from . import views
# from backtest_implementation_ninja.validate_trades.main import *
# from x_twitter_crypto_news.main import *

# from .views import generate_pdf



urlpatterns = [
    path("api/", api.urls),
    # The home page
    path('', views.index, name='home'),

    # Specific paths for individual templates
    path('index/', TemplateView.as_view(template_name='home/index.html')),
    path('backtest/', TemplateView.as_view(template_name='home/backtest.html')),
    path('charts/', TemplateView.as_view(template_name='home/charts.html')),
    path('cointegration-dashboard/', TemplateView.as_view(template_name='home/cointegration-dashboard.html')),
    path('transaction_logs/', TemplateView.as_view(template_name='home/transaction_logs.html')),
    # path('report/', generate_pdf, name='generate_pdf'),

    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

    # don't add endpoint if have route in views.

    # Additional paths for other views
    # path('get_data/', views.get_data, name='get_data'),
    # path('bar_chart/', views.bar_chart, name='bar_chart'),
    # path('get_filtered_data/', views.post_filter_trades_by_date_range, name='get_filtered_data'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# urlpatterns += static('/models/', document_root=os.path.abspath(r"..\financialDashboard\backtest_implementation_ninja\validate_trades\models\ATOMUSDT\ATOMUSDT_P0501\ATOMUSDT_115"))