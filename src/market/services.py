from django.db.models import (
    Avg, 
    F,
    RowRange,
    Window,
    Max,
    Min,
    ExpressionWrapper,
    DecimalField,
    Case,
    When,
    Value
)
from django.db.models.functions import TruncDate, FirstValue, Lag, Coalesce
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal


from market.models import StockQuote


def get_daily_stock_quotes_queryset(ticker, days=28, use_bucket=False):
    now = timezone.now()
    start_date = now - timedelta(days=days)
    end_date = now
    lastest_daily_timestamps = (
        StockQuote.objects.filter(company__ticker=ticker, time__range=(start_date - timedelta(days=40), end_date))
        .annotate(date=TruncDate('time'))
        .values('company', 'date')
        .annotate(latest_time=Max('time'))
        .values('company', 'date', 'latest_time')
        .order_by('date')
    )
    acutal_timestamps = [x['latest_time'] for x in lastest_daily_timestamps]
    qs = StockQuote.timescale.filter(
        company__ticker=ticker, 
        time__range=(start_date, end_date),
        time__in=acutal_timestamps
    )
    if use_bucket:
        return qs.time_bucket('time', '1 day')
    return qs



def get_daily_moving_averages(ticker, days=28, queryset=None):
    if queryset is None:
        queryset = get_daily_stock_quotes_queryset(ticker=ticker, days=days)
    obj = queryset.annotate(
            ma_5=Window(
                expression=Avg('close_price'),
                order_by=F('time').asc(),
                partition_by=[],
                frame=RowRange(start=-4, end=0),
            ),
            ma_20=Window(
                expression=Avg('close_price'),
                order_by=F('time').asc(),
                partition_by=[],
                frame=RowRange(start=-19, end=0),
            )
    ).order_by('-time').first()
    if not obj:
        return None
    ma_5 = obj.ma_5
    ma_20 = obj.ma_20
    if ma_5 is None or ma_20 is None:
        return None
    if ma_5 <= 0 or ma_20 <= 0:
        return None
    return {
        "ma_5":  float(round(ma_5, 4)),
        "ma_20":  float(round(ma_20, 4))
    }


def get_price_target(ticker, days=28, queryset=None):
    """
    Simplified price target calculation
    """
    if queryset is None:
        queryset = get_daily_stock_quotes_queryset(ticker, days=days)    
    daily_data = (
        queryset
        .annotate(
            latest_price=Window(
                expression=FirstValue('close_price'),
                partition_by=[],
                order_by=F('time').desc()
            )
        )
        .aggregate(
            current_price=Max('latest_price'),
            avg_price=Avg('close_price'),
            highest=Max('high_price'),
            lowest=Min('low_price')
        )
    )
    
    if not daily_data:
        return None
    current_price = float(daily_data['current_price'])
    avg_price = float(daily_data['avg_price'])
    price_range = float(daily_data['highest']) - float(daily_data['lowest'])
    
    # Simple target based on average price and recent range
    conservative_target = current_price + (price_range * 0.382)  # 38.2% Fibonacci
    aggressive_target = current_price + (price_range * 0.618)   # 61.8% Fibonacci
    
    return {
        'current_price': round(current_price, 4),
        'conservative_target': round(conservative_target, 4),
        'aggressive_target':  round(aggressive_target, 4),
        'average_price':  round(avg_price, 4)
    }

def get_volume_trend(ticker, days=28, queryset=None):
    """
    Analyze recent volume trends
    """
    if queryset is None:
        queryset = get_daily_stock_quotes_queryset(ticker=ticker, days=days)
    start = -(days - 1)
    data = queryset.annotate(
        avg_volume=Window(
            expression=Avg('volume'),
            order_by=F('time').asc(),
            partition_by=[],
            frame=RowRange(start=start, end=0)
        )
    ).order_by('-time').first()

    if not data:
        return None
    vol = data.volume
    avg_vol = data.avg_volume
    volume_change = 0
    if vol is None or avg_vol is None:
        return None
    if vol > 0 and avg_vol > 0:
        volume_change = (( vol - avg_vol) / avg_vol) * 100
    return {
        'avg_volume': float(avg_vol),
        'latest_volume': int(vol),
        'volume_change_percent': float(volume_change)
    }

def calculate_rsi(ticker, days=28, queryset=None, period=14):
    """
    Calculate Relative Strength Index (RSI) using Django ORM.
    
    Args:
        ticker (str): Stock ticker symbol
        days (int): Days in the price data (default: 28)
        queryset (list): Stock Quote querset
        period (int): RSI period (default: 14)
        
    Returns:
        dict: RSI value and component calculations
    """
    # Get daily price data
    if period is None:
        period = int(days / 4)
    if queryset is None:
        queryset = get_daily_stock_quotes_queryset(ticker, days=days, use_bucket=True)

    
    # Calculate price changes and gains/losses with explicit decimal conversion
    movement = queryset.annotate(
        closing_price=ExpressionWrapper(
            F('close_price'),
            output_field=DecimalField(max_digits=10, decimal_places=4)
        ),
        prev_close=Window(
            expression=Lag('close_price'),
            order_by=F('bucket').asc(),
            partition_by=[],
            output_field=DecimalField(max_digits=10, decimal_places=4)
        )
    ).annotate(
        price_change=ExpressionWrapper(
            F('close_price') - F('prev_close'),
            output_field=DecimalField(max_digits=10, decimal_places=4)
        ),
        gain=Case(
            When(price_change__gt=0, 
                 then=ExpressionWrapper(
                     F('price_change'),
                     output_field=DecimalField(max_digits=10, decimal_places=4)
                 )),
            default=Value(0, output_field=DecimalField(max_digits=10, decimal_places=4)),
            output_field=DecimalField(max_digits=10, decimal_places=4)
        ),
        loss=Case(
            When(price_change__lt=0,
                 then=ExpressionWrapper(
                     -F('price_change'),
                     output_field=DecimalField(max_digits=10, decimal_places=4)
                 )),
            default=Value(0, output_field=DecimalField(max_digits=10, decimal_places=4)),
            output_field=DecimalField(max_digits=10, decimal_places=4)
        )
    )
    
    # Calculate initial averages for the first period
    initial_avg = movement.exclude(prev_close__isnull=True)[:period].aggregate(
        avg_gain=Coalesce(
            ExpressionWrapper(
                Avg('gain'),
                output_field=DecimalField(max_digits=10, decimal_places=4)
            ),
            Value(0, output_field=DecimalField(max_digits=10, decimal_places=4))
        ),
        avg_loss=Coalesce(
            ExpressionWrapper(
                Avg('loss'),
                output_field=DecimalField(max_digits=10, decimal_places=4)
            ),
            Value(0, output_field=DecimalField(max_digits=10, decimal_places=4))
        )
    )
    
    # Get subsequent data points for EMA calculation
    subsequent_data = list(movement.exclude(prev_close__isnull=True)[period:].values('gain', 'loss'))
    
    # Calculate EMA-based RSI
    avg_gain = initial_avg['avg_gain']
    avg_loss = initial_avg['avg_loss']
    alpha = Decimal(1 / period)  # Smoothing factor
    
    # Update moving averages using EMA formula
    for data in subsequent_data:
        avg_gain = (avg_gain * (1 - alpha) + data['gain'] * alpha)
        avg_loss = (avg_loss * (1 - alpha) + data['loss'] * alpha)
    
    # Prevent division by zero
    if avg_loss == 0:
        rsi = 100
    else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
    
    return {
        'rsi': round(float(rsi), 4),
        'avg_gain': round(float(avg_gain), 4),
        'avg_loss': round(float(avg_loss), 4),
        'period': period,
        'days': days,
    }