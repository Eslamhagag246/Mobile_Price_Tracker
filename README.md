# 📱 Mobile Phone Price Tracker

A data-driven web application that tracks mobile phone prices across major Egyptian e-commerce websites, forecasts prices for the next 7 days, and helps users decide the best time to buy.

---

## 🌐 Live Demo

👉 [Open the App](#) *(Add your Streamlit URL here after deployment)*

---

## 💡 Project Idea

The goal of this project is to help users make smarter purchasing decisions by answering two key questions:

- **How has this phone's price changed over time?**
- **Is now a good time to buy, or should I wait?**

To answer these questions, price data was scraped from 5 major Egyptian e-commerce websites over a period of ~2 months, covering 10 phone brands across 480 unique product listings.

---

## 🔍 Features

### 🔎 Product Forecast Tab
- Search for any phone by name, brand, or website
- View current price, average price, min/max range
- Get a **7-day price forecast** with confidence band
- See **tomorrow's expected price** and how it compares to today
- Receive a smart **buy signal**:
  - 🟢 Good Time to Buy
  - 🔴 Wait — Price May Drop
  - 🔴 Price Rising — Buy Soon
  - 🟡 Price is Stable
- Interactive price history chart with forecast overlay
- Price distribution and daily volatility charts
- Full 7-day forecast table with low/high price estimates
- Direct product link to the website

### 📊 Data Overview Tab
- Dataset statistics (total records, unique products, date range, websites tracked)
- Average price trends by brand over time
- Price range comparison across websites (box plot)
- Distribution of price observations per product

### 📈 Market Insights Tab
- Top 5 biggest price drops since tracking started
- Top 5 biggest price rises since tracking started
- Horizontal bar chart of all price changes across products

---

## 🛠️ How It Works

### Data Collection
Price data was scraped from 5 websites:
- **Jumia** (9,156 records)
- **Dream2000** (647 records)
- **BTECH** (380 records)
- **2B** (265 records)
- **Dubaiphone** (56 records)

**Total: 10,504 price observations**

### Brands Tracked
Apple · Samsung · Xiaomi · Honor · Oppo · Realme · Infinix · Vivo · Tecno · Redmi

### Preprocessing
- Cleaned and normalized price, brand, website, and timestamp fields
- Averaged duplicate prices scraped on the same day for the same product
- Created a unique product identity per listing (product name + website)
- Engineered time-based features: day index, rolling average, volatility, % change

### Forecasting Model
A per-product time-series regression approach:
- **Linear Regression** for products with fewer than 10 observations
- **Polynomial Regression (degree 2)** for products with 10+ observations
- Forecast clipped to realistic price bounds (±50% of historical range)
- Confidence band based on mean absolute error of the fit
- Confidence level assigned based on number of available data points (Low / Medium / High)

### Buy Signal Logic
The buy signal is calculated from two factors:
1. **Current price vs historical average** — is it currently cheap or expensive?
2. **Forecasted trend** — is the price expected to go up or down?

---

## 📦 Tech Stack

| Tool | Purpose |
|---|---|
| Python | Core language |
| Pandas | Data manipulation |
| NumPy | Numerical operations |
| Scikit-learn | Linear & Polynomial Regression |
| Plotly | Interactive charts |
| Streamlit | Web application framework |
| GitHub | Version control & deployment |
| Streamlit Cloud | Free app hosting |

---

## 🗂️ Project Structure

```
mobile_price_tracker/
│
├── mobile_streamlit_app.py   # Main Streamlit web application
├── mobile_phones_cleaned.csv # Cleaned scraped price dataset
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

---

## 📊 Dataset Statistics

- **Total records**: 10,504
- **Unique products**: 480
- **Date coverage**: December 14, 2025 → February 8, 2026 (56 days)
- **Products with 5+ observations**: 195
- **Products with 10+ observations**: 98
- **Products with 20+ observations**: 29

---

## ⚠️ Limitations

- Data covers ~56 days — longer history would improve forecast accuracy
- Most products have 3-5 price observations, so forecasts are based on short trends
- Confidence is shown transparently (Low / Medium / High) so users know how much to rely on the forecast
- Prices are in **Egyptian Pounds (EGP)**

---

## 🚀 Deployment Instructions

1. Create a new GitHub repository
2. Upload these files:
   - `mobile_streamlit_app.py`
   - `mobile_phones_cleaned.csv`
   - `requirements.txt`
   - `README.md`
3. Go to [share.streamlit.io](https://share.streamlit.io)
4. Sign in with GitHub
5. Click "New app" and select your repository
6. Set main file to `mobile_streamlit_app.py`
7. Click "Deploy"

---

## 👨‍💻 Author

Built by **Eslamhagag246**
