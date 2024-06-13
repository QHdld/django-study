from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse
import json

from financial_info_for_front import MarketDataFetcher, ExchangeRateDataFetcher, GoldPriceFetcher, StockNameConverter, StockDataFetcher
from prediction_model import get_prediction_data

def market_data_view(request):
    market_fetcher = MarketDataFetcher()
    market_data = market_fetcher.get_market_prices_for_ui()

    exchange_fetcher = ExchangeRateDataFetcher('nfiQF5JrJm7RKRpZfaqjyaLXdRccy7pQm2rI3BYf')
    exchange_data = exchange_fetcher.get_all_exchange_rates()

    gold_fetcher = GoldPriceFetcher()
    gold_data = gold_fetcher.get_gold_price()

    context = {**market_data, **exchange_data, **gold_data}
    return render(request, 'myapp/market_data.html', context)

@csrf_exempt
def show_chart(request):
    if request.method == "POST":
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        stock_name = body.get('stock_name')
        converter = StockNameConverter()
        stock_code = converter.convert_name_to_code(stock_name)
        
        if stock_code:
            data_fetcher = StockDataFetcher()
            labels, data = data_fetcher.get_stock_data(stock_code)
            return JsonResponse({
                'labels': labels,
                'data': data,
            })
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def get_prediction_view(request):
    if request.method == "POST":
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        stock_name = body.get('stock_name')
        converter = StockNameConverter()
        stock_code = converter.convert_name_to_code(stock_name)

        if stock_code:
            data = get_prediction_data(stock_code)
            return JsonResponse(data)
    return JsonResponse({'error': 'Invalid request'}, status=400)
