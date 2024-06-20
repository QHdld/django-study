import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from prediction_model import get_prediction_data
from financial_info_for_front import MarketDataFetcher, ExchangeRateDataFetcher, GoldPriceFetcher, StockDataFetcher, StockNameConverter

logger = logging.getLogger(__name__)

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
        stock_name = request.POST.get('stock_name')
        logger.debug(f"Received stock_name: {stock_name}")
        if not stock_name:
            return JsonResponse({'error': 'No stock name provided'}, status=400)
        
        converter = StockNameConverter()
        stock_code = converter.convert_name_to_code(stock_name)
        
        if not stock_code:
            return JsonResponse({'error': 'Invalid stock name'}, status=400)

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
        try:
            stock_name = request.POST.get('stock_name')
            logger.debug(f"Received stock_name: {stock_name}")
            if not stock_name:
                return JsonResponse({'error': 'No stock name provided'}, status=400)
            
            converter = StockNameConverter()
            stock_code = converter.convert_name_to_code(stock_name)
            
            if not stock_code:
                return JsonResponse({'error': 'Invalid stock name'}, status=400)

            prediction_data = get_prediction_data(stock_code)
            logger.debug(f"Prediction data: {prediction_data}")
            return JsonResponse(prediction_data)
        except Exception as e:
            logger.error(f"Error in get_prediction_view: {e}")
            return JsonResponse({'error': 'An error occurred'}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)
