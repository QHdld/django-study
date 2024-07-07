import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from prediction_model import get_prediction_data
from financial_info_for_front import MarketDataFetcher, ExchangeRateDataFetcher, GoldPriceFetcher, StockDataFetcher, StockNameConverter
import pandas as pd

logger = logging.getLogger(__name__)

def market_data_view(request):
    market_fetcher = MarketDataFetcher()
    market_data = market_fetcher.get_market_prices_for_ui()

    exchange_fetcher = ExchangeRateDataFetcher()
    exchange_data = exchange_fetcher.get_all_exchange_rates()

    gold_fetcher = GoldPriceFetcher()
    gold_data = gold_fetcher.get_gold_price()

    context = {**market_data, **exchange_data, **gold_data}
    return render(request, 'myapp/market_data.html', context)

@csrf_exempt
def show_chart(request):
    if request.method == "POST":
        stock_names = request.POST.getlist('stock_names')
        date_range = request.POST.get('date_range')
        logger.debug(f"Received stock_names: {stock_names}, date_range: {date_range}")

        if not stock_names:
            return JsonResponse({'error': 'No stock names provided'}, status=400)
        
        converter = StockNameConverter()
        stock_codes = [converter.convert_name_to_code(stock_name) for stock_name in stock_names]
        
        if None in stock_codes:
            return JsonResponse({'error': 'Invalid stock name(s)'}, status=400)

        # 기간 범위에 따른 시작 날짜 계산
        end_date = pd.to_datetime('today')
        if date_range == '5y':
            start_date = end_date - pd.DateOffset(years=5)
        elif date_range == '3y':
            start_date = end_date - pd.DateOffset(years=3)
        elif date_range == '1y':
            start_date = end_date - pd.DateOffset(years=1)
        elif date_range == '6m':
            start_date = end_date - pd.DateOffset(months=6)
        else:
            return JsonResponse({'error': 'Invalid date range'}, status=400)

        data_fetcher = StockDataFetcher()
        all_data = []
        for stock_code in stock_codes:
            labels, data = data_fetcher.get_stock_data(stock_code, start_date, end_date)
            all_data.append({'stock_code': stock_code, 'labels': labels, 'data': data})

        return JsonResponse({'all_data': all_data})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def get_prediction_view(request):
    if request.method == "POST":
        try:
            stock_name = request.POST.get('stock_name')
            date_range = request.POST.get('date_range')
            logger.debug(f"Received stock_name: {stock_name}, date_range: {date_range}")

            if not stock_name:
                return JsonResponse({'error': 'No stock name provided'}, status=400)
            
            converter = StockNameConverter()
            stock_code = converter.convert_name_to_code(stock_name)
            
            if not stock_code:
                return JsonResponse({'error': 'Invalid stock name'}, status=400)

            # 기간 범위에 따른 시작 날짜 계산
            end_date = pd.to_datetime('today')
            if date_range == '5y':
                start_date = end_date - pd.DateOffset(years=5)
            elif date_range == '3y':
                start_date = end_date - pd.DateOffset(years=3)
            elif date_range == '1y':
                start_date = end_date - pd.DateOffset(years=1)
            elif date_range == '6m':
                start_date = end_date - pd.DateOffset(months=6)
            else:
                return JsonResponse({'error': 'Invalid date range'}, status=400)

            logger.debug(f"Fetching prediction data from {start_date} to {end_date}")
            prediction_data = get_prediction_data(stock_code, start_date, end_date)
            logger.debug(f"Prediction data: {prediction_data}")
            return JsonResponse(prediction_data)
        except Exception as e:
            logger.error(f"Error in get_prediction_view: {e}")
            return JsonResponse({'error': f'An error occurred: {e}'}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)
