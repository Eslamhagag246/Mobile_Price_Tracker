import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_absolute_error, r2_score
from datetime import timedelta
import warnings
warnings.filterwarnings('ignore')


# ─────────────────────────────────────────
# 1. DATA LOADING & PREPROCESSING
# ─────────────────────────────────────────
def load_and_preprocess_data(filepath='mobile_cleaned_continuous.csv'):
    df = pd.read_csv(filepath)

    # Clean price
    df['price'] = df['price'].astype(str)
    df['price'] = df['price'].str.replace('EGP', '', regex=False)
    df['price'] = df['price'].str.replace(',', '', regex=False)
    df['price'] = df['price'].str.strip()
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df = df.dropna(subset=['price'])

    # Normalize text
    df['brand']   = df['brand'].str.lower().str.strip()
    df['website'] = df['website'].str.lower().str.strip()
    df['name']    = df['name'].str.strip()
    
    # Parse timestamp
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%m/%d/%Y', errors='coerce')
    df['date']      = df['timestamp'].dt.date
    df['date']      = pd.to_datetime(df['date'])

    # Product key: name + website + RAM + storage
    df['product_key'] = (
        df['name'].str.lower().str.strip() + ' ' +
        df['website'].str.lower() + ' ' +
        df['ram_gb'].astype(str) + ' ' +
        df['storage_gb'].astype(str)
    )

    # Daily average
    df_daily = df.groupby(['product_key', 'date']).agg(
        price     = ('price',   'mean'),
        name      = ('name',    'first'),
        brand     = ('brand',   'first'),
        website   = ('website', 'first'),
        ram_gb    = ('ram_gb',  'first'),
        storage_gb= ('storage_gb','first'),
        URL       = ('URL',     'last'),
        timestamp = ('timestamp','first')
    ).reset_index()

    df_daily = df_daily.sort_values(['product_key','date'])

    return df_daily
# ─────────────────────────────────────────
# 2. FEATURE ENGINEERING
# ─────────────────────────────────────────
def engineer_features(pdf):
    pdf = pdf.sort_values('date').copy()
    
    # Time features
    pdf['day_index']   = (pdf['date'] - pdf['date'].min()).dt.days
    pdf['dayofweek']   = pdf['date'].dt.dayofweek
    pdf['rolling_avg'] = pdf['price'].rolling(window=3, min_periods=1).mean()
    pdf['pct_change']  = pdf['price'].pct_change().fillna(0)
    pdf['volatility']  = pdf['price'].rolling(window=3, min_periods=1).std().fillna(0)
    
    # ✅ Device specs features (normalized)
    pdf['ram_normalized'] = pdf['ram_gb'] / 16.0  # Normalize to 0-1 (max 16GB)
    pdf['storage_normalized'] = pdf['storage_gb'] / 1024.0  # Normalize to 0-1 (max 1TB)
    
    # ✅ Specs value score (higher specs = higher expected price)
    pdf['specs_score'] = (pdf['ram_gb'] / 4.0) + (pdf['storage_gb'] / 128.0)
    
    return pdf
# ─────────────────────────────────────────
# 3. FORECASTING MODEL
# ─────────────────────────────────────────
def forecast_product(pdf, days_ahead=7):
    pdf = engineer_features(pdf)
    n = len(pdf)

    # ✅ Features: time + device specs
    X = pdf[['day_index', 'ram_normalized', 'storage_normalized', 'specs_score']].values
    y = pdf['price'].values

    last_day   = pdf['day_index'].max()
    last_price = pdf['price'].iloc[-1]
    avg_price  = pdf['price'].mean()
    min_price  = pdf['price'].min()
    max_price  = pdf['price'].max()
    
    # Get device specs for future predictions (same as current)
    ram_norm = pdf['ram_normalized'].iloc[-1]
    storage_norm = pdf['storage_normalized'].iloc[-1]
    specs = pdf['specs_score'].iloc[-1]

    # Model selection
    if n >= 10:
        poly   = PolynomialFeatures(degree=2)
        X_poly = poly.fit_transform(X)
        model  = LinearRegression().fit(X_poly, y)
        y_fit  = model.predict(X_poly)
        
        # Future predictions with same RAM/storage
        future_X = np.array([
            [last_day + i, ram_norm, storage_norm, specs] 
            for i in range(1, days_ahead + 1)
        ])
        future_poly = poly.transform(future_X)
        forecast    = model.predict(future_poly)
        model_type  = "polynomial"
    else:
        model    = LinearRegression().fit(X, y)
        y_fit    = model.predict(X)
        
        future_X = np.array([
            [last_day + i, ram_norm, storage_norm, specs] 
            for i in range(1, days_ahead + 1)
        ])
        forecast = model.predict(future_X)
        model_type = "linear"

    # Metrics
    residuals = np.abs(y - y_fit)
    mae = residuals.mean()
    std = residuals.std() if len(residuals) > 1 else mae

    # Clip forecast to realistic bounds
    forecast = np.clip(forecast, min_price * 0.5, max_price * 1.5)

    # Forecast dates
    today = pd.Timestamp.today().normalize()
    forecast_dates = [today + timedelta(days=i) for i in range(1, days_ahead + 1)]

    # Confidence based on number of observations
    if n >= 15:
        confidence = "High"
    elif n >= 7:
        confidence = "Medium"
    else:
        confidence = "Low"

    # Buy signal logic
    price_vs_avg = (last_price - avg_price) / avg_price * 100
    trend_pct = (forecast[-1] - last_price) / last_price * 100

    if price_vs_avg <= -3 and trend_pct >= 0:
        signal = "buy"
        signal_text = "🟢 Good Time to Buy"
        signal_desc = f"Current price is {abs(price_vs_avg):.1f}% below average and is expected to rise. Buy now before it goes up."
    elif price_vs_avg >= 3 and trend_pct < 0:
        signal = "wait"
        signal_text = "🔴 Wait — Price May Drop"
        signal_desc = f"Current price is {price_vs_avg:.1f}% above average and the trend shows it may decrease. Consider waiting."
    elif abs(trend_pct) <= 2:
        signal = "neutral"
        signal_text = "🟡 Price is Stable"
        signal_desc = f"Price is not expected to change significantly in the next {days_ahead} days. Current price is close to the average."
    elif trend_pct > 2:
        signal = "wait"
        signal_text = "🔴 Price Rising — Buy Soon or Wait"
        signal_desc = f"Price is trending upward (~{trend_pct:.1f}% over {days_ahead} days). Buy soon if you need it, or wait for a potential correction."
    else:
        signal = "buy"
        signal_text = "🟢 Price is Dropping — Good Time to Buy"
        signal_desc = f"Price is expected to drop ~{abs(trend_pct):.1f}% over the next {days_ahead} days."

    return {
        'pdf'            : pdf,
        'forecast_dates' : forecast_dates,
        'forecast_prices': forecast,
        'mae'            : mae,
        'std'            : std,
        'confidence'     : confidence,
        'signal'         : signal,
        'signal_text'    : signal_text,
        'signal_desc'    : signal_desc,
        'last_price'     : last_price,
        'avg_price'      : avg_price,
        'min_price'      : min_price,
        'max_price'      : max_price,
        'trend_pct'      : trend_pct,
        'n_obs'          : n,
        'model_type'     : model_type,
        'price_vs_avg'   : price_vs_avg,
    }
# ─────────────────────────────────────────
# 4. BATCH FORECASTING (Optional)
# ─────────────────────────────────────────
def forecast_all_products(df_daily, min_obs=3):
  
    forecasts = {}
    
    for key, grp in df_daily.groupby('product_key'):
        if len(grp) < min_obs:
            continue
        try:
            forecasts[key] = forecast_product(grp)
        except:
            continue
    return forecasts
