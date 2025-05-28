import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
import matplotlib.pyplot as plt

# ——— AYARLANABİLİR PARAMETRELER ———
ticker     = 'MAVI.IS'         # İncelemek istediğin BIST kodu
start_date = '2021-01-01'       # Başlangıç tarihi (YYYY-MM-DD)
end_date   = '2025-04-01'       # Bitiş tarihi (YYYY-MM-DD)
# ——————————————————————————————

# 1) VERİ ÇEKME
df = yf.download(ticker,
                 start=start_date,
                 end=end_date,
                 auto_adjust=True)  # %100 kapanış fiyatına göre düzeltilmiş

# 2) CLOSE SERİSİNİ 1D HALİNE GETİRME
close = df['Close']
# Eğer hala 2 boyutlu geldiyse (shape: (n,1)), düzleştir:
if hasattr(close, "ndim") and close.ndim > 1:
    close = close.iloc[:, 0]
# Artık kesinlikle pd.Series

# 3) RSI HESAPLAMA
rsi = RSIIndicator(close).rsi()
df['rsi'] = rsi

# 4) AL / SAT SİNYALLERİ
df['buy_signal']  = df['rsi'] < 30
df['sell_signal'] = df['rsi'] > 70

# 5) GRAFİK
plt.figure(figsize=(14, 7))

# Fiyat
plt.subplot(2, 1, 1)
plt.plot(df.index, close, label=f'{ticker} Kapanış', linewidth=1)
plt.title(f'{ticker} Fiyat Grafiği ({start_date} → {end_date})')
plt.legend()

# RSI
plt.subplot(2, 1, 2)
plt.plot(df.index, df['rsi'], label='RSI', linewidth=1)
plt.axhline(30, linestyle='--', label='RSI = 30 (AL)',   alpha=0.6)
plt.axhline(70, linestyle='--', label='RSI = 70 (SAT)',  alpha=0.6)
# AL/SAT işaretleri
plt.scatter(df.index[df['buy_signal']],  df['rsi'][df['buy_signal']],  marker='^', label='AL',  s=50)
plt.scatter(df.index[df['sell_signal']], df['rsi'][df['sell_signal']], marker='v', label='SAT', s=50)
plt.title('RSI ve AL/SAT Sinyalleri')
plt.legend()

plt.tight_layout()
plt.show()

# 6) SON VERİLERİ İNCELE
print(df[['Close', 'rsi', 'buy_signal', 'sell_signal']].tail())
