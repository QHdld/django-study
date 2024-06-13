from django.urls import path
from .views import market_data_view, show_chart, get_prediction_view

urlpatterns = [
    path('', market_data_view, name='market_data'),
    path('show_chart/', show_chart, name='show_chart'),
    path('get_prediction/', get_prediction_view, name='get_prediction'),
]
