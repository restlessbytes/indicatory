# Indicatory

The purpose behind this project is to compile a collection of stock indicators, along with related concepts

Additionally, although the focus of this project is on indicators, it also includes functions and entities that aren't strictly indicators such as Candlestick charts, SVN (support vector machines), ARIMA models and also implementations of ideas and sketches that I've come up with on my own.

Examples and use cases in the form of Jupyter notebooks can be found in `notebooks/`.

All examples use AMD stock data for no particular reason.

### Motivation

* I've been keeping an eye on [`polars`](https://docs.pola.rs/) for quite some time now and this project provided me with the perfect opportunity to explore its capabilities (and short-commings?) a bit, especially since stock data are typically structured in "dataframes". 
* I like playing around with financial (read: stocks) data from time to time; however, I couldn't find a indicator library that met all of my needs.
* [Just for Fun. No, Really:)](https://justforfunnoreally.dev/) :rocket:

## Indicators

### Implemented

* [x] Base Chart: Candlesticks + Volume
* [x] Moving Averages (simple, exponential)
* [x] Moving Median
* [x] Moving Average Convergence / Divergence (MACD)
* [x] On-Balance Volume (OBV)
* [x] Percentage Price Oscillator (PPO)
* [x] Stochastic Oscillators (fast, slow)
* [x] Relative Strength Indicator (RSI)
* [x] (Average) True Range (ATR)
* [x] Stat Indicators: Standard Deviation, Variance
* [x] Average / Mean Absolute Deviation (AAD, MAD)
* [x] Standard Deviation bands, AAD / MAD bands
* [x] Price-by-Volume (PV)
* [x] Daily Range
* [x] Daily Change / Returns
* [x] OHLC Average Price (AVG Price)
* [x] Relative Currency Strength (RSC)

### In progress 

* [ ] LOESS regression, exponential smoothing (Holt-Winters)
* [ ] Stationarity, Auto-Regression (AR) -> AR(I)MA
* [ ] Average Directional Index (ADX)
* [ ] Parabolic SAR
* [ ] Heiken Ashi - Candlesticks ("naive implementation")
* [ ] Volume and Moving Average
* [ ] Price on EP events (reports, dividends etc.)
* [ ] "Open-Close" / "High-Low" Candlesticks
* [ ] "Open-Close" timeseries (Pairs of "open-close")
* [ ] Day-of-Week Significance
* [ ] Regression Lines (linear, polynomial)
* [ ] Support Vector Regression

## Resources

For definitions, formulas, and algorithms related to indicators, I've mostly consulted their corresponding Wikipedia article or the docs on [Stockcharts:Chartschool](https://chartschool.stockcharts.com/).

As for ARIMA models and related concepts, their implementation is currently underway. 
For this aspect of the library, I found the following sites and resources particularly helpful:

* https://www.ibm.com/topics/arima-model
* https://www.statsmodels.org/stable/examples/notebooks/generated/tsa_arma_1.html
* [Time Series (including ARIMA models) by Aric LaBarr](https://www.youtube.com/playlist?list=PLjwX9KFWtvNnOc4HtsvaDf1XYG3O5bv5s)
