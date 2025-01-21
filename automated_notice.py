import asyncio
import pandas as pd
import ccxt
from telegram import Bot

# Initialize Binance Exchange with time adjustment
exchange = ccxt.binance({
    'enableRateLimit': True,
    'options': {
        'adjustForTimeDifference': True,  # Automatically adjust for time difference
    },
})

# Set up Telegram Bot
TELEGRAM_TOKEN = '7750247970:AAFtWXruDNWGbBp8h1DVGZRiw9FtwGHVNJk'
CHAT_ID = '-1002456402470'
bot = Bot(token=TELEGRAM_TOKEN)

# Asynchronous function to send Telegram messages
async def send_telegram_message(message):
    await bot.send_message(chat_id=CHAT_ID, text=message)

# Function to fetch OHLCV data from an exchange
async def fetch_ohlcv(symbol, limit):
    return exchange.fetch_ohlcv(symbol, timeframe='1d', limit=limit)

# Function to detect volume outliers based on a given window size
def detect_volume_outliers(df, window_size, std_multiplier):
    if len(df) < window_size:
        raise ValueError(f"Not enough data to analyze the past {window_size} days.")

    # Calculate rolling average and standard deviation for the given window size
    df['Volume_Mean'] = df['volume'].rolling(window=window_size).mean()
    df['Volume_Std'] = df['volume'].rolling(window=window_size).std()
    df['Volume_Threshold'] = df['Volume_Mean'] + std_multiplier * df['Volume_Std']
    df['Volume_Outlier'] = df['volume'] > df['Volume_Threshold']

    return df

# Asynchronous function to monitor symbols for volume outliers day by day
async def monitor_symbols(symbols, window_size=10, std_multiplier=2.5):
    for symbol in symbols:
        try:
            # Fetch OHLCV data for the specified window size
            ohlcv = await fetch_ohlcv(symbol, limit=window_size + 10)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['Date'] = pd.to_datetime(df['timestamp'], unit='ms')

            # Detect outliers day by day
            df = detect_volume_outliers(df, window_size, std_multiplier)

            # Log results for this symbol
            print(f"Results for {symbol}:")
            print("Past Data:")
            print(df[['Date', 'volume', 'Volume_Mean', 'Volume_Std', 'Volume_Threshold', 'Volume_Outlier']])

             # Check if the latest data is an outlier and if it's for today
            latest_row = df.iloc[-1]
            today_date = pd.Timestamp.now().normalize()
            if latest_row['Volume_Outlier'] and latest_row['Date'].normalize() == today_date:
                await send_telegram_message(
                    f"Volume outlier detected for {symbol} today ({latest_row['Date']}). Volume: {latest_row['volume']}, Threshold: {latest_row['Volume_Threshold']}. You can buy now. win rate is around 60% for holding 1 day."
                )
            else:
                print(f"No volume outlier for {symbol} today ({latest_row['Date']}).")

        except Exception as e:
            print(f"Error occurred for {symbol}: {e}")

# Main function to monitor multiple symbols
async def main():
    symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'ADA/USDT']  # List of symbols to monitor
    await monitor_symbols(symbols, window_size=10, std_multiplier=2.5)

# Run the script
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Script was interrupted by the user.")
