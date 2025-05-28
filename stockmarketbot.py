import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
import matplotlib.pyplot as plt

# ——————————————————————————————
ticker     = 'MAVI.IS'          
start_date = '2021-01-01'       
end_date   = '2025-04-01'       
# ——————————————————————————————
df = yf.download(ticker,
                 start=start_date,
                 end=end_date,
                 auto_adjust=True) 

close = df['Close']
if hasattr(close, "ndim") and close.ndim > 1:
    close = close.iloc[:, 0]
rsi = RSIIndicator(close).rsi()
df['rsi'] = rsi
df['buy_signal']  = df['rsi'] < 30
df['sell_signal'] = df['rsi'] > 70
plt.figure(figsize=(14, 7))
plt.subplot(2, 1, 1)
plt.plot(df.index, close, label=f'{ticker} Kapanış', linewidth=1)
plt.title(f'{ticker} Fiyat Grafiği ({start_date} → {end_date})')
plt.legend()
plt.subplot(2, 1, 2)
plt.plot(df.index, df['rsi'], label='RSI', linewidth=1)
plt.axhline(30, linestyle='--', label='RSI = 30 (AL)',   alpha=0.6)
plt.axhline(70, linestyle='--', label='RSI = 70 (SAT)',  alpha=0.6)
plt.scatter(df.index[df['buy_signal']],  df['rsi'][df['buy_signal']],  marker='^', label='AL',  s=50)
plt.scatter(df.index[df['sell_signal']], df['rsi'][df['sell_signal']], marker='v', label='SAT', s=50)
plt.title('RSI ve AL/SAT Sinyalleri')
plt.legend()
plt.tight_layout()
plt.show()
print(df[['Close', 'rsi', 'buy_signal', 'sell_signal']].tail())
