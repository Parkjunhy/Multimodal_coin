# import os
# from dotenv import load_dotenv
# import tweepy
# import requests
# from binance.client import Client
# import pandas as pd
# from datetime import datetime, timedelta
# import openai
# import time
# import schedule

# # Load environment variables
# load_dotenv()

# # API Keys from .env
# # CRYPTONEWS_API_KEY = os.getenv('CRYPTONEWS_API_KEY')
# TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
# TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
# TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
# TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
# BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
# BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')
# OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# # Initialize API clients
# def initialize_clients():
#     # Twitter API setup
#     auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
#     auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
#     twitter_client = tweepy.API(auth)
    
#     # Binance API setup
#     binance_client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
    
#     # OpenAI setup
#     openai.api_key = OPENAI_API_KEY
    
#     return twitter_client, binance_client

# def get_deepsearch_news():
#     url = f"https://api-v2.deepsearch.com"
#     response = requests.get(url)
#     return response.json()['data']

# def get_twitter_sentiment():
#     twitter_client, _ = initialize_clients()
#     tweets = twitter_client.search_tweets(q="bitcoin BTC", lang="en", count=100)
#     return [tweet.text for tweet in tweets]

# def get_btc_market_data():
#     _, binance_client = initialize_clients()
    
#     # Get historical klines/candlestick data
#     klines = binance_client.get_historical_klines(
#         "BTCUSDT", 
#         Client.KLINE_INTERVAL_1HOUR,
#         str(int((datetime.now() - timedelta(days=7)).timestamp() * 1000))
#     )
    
#     # Convert to DataFrame
#     df = pd.DataFrame(klines, columns=[
#         'timestamp', 'open', 'high', 'low', 'close', 
#         'volume', 'close_time', 'quote_asset_volume',
#         'number_of_trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'
#     ])
    
#     df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
#     return df

# def analyze_with_gpt(news, tweets, market_data, trading_history):
#     system_prompt = """You are an expert cryptocurrency trading analyst with deep knowledge of Bitcoin markets, technical analysis, and sentiment analysis. Your role is to:

# 1. Analyze market data, news, and social sentiment to make informed trading decisions
# 2. Consider multiple factors including:
#    - Technical indicators from price data
#    - Market sentiment from news and social media
#    - Historical trading patterns
#    - Risk management principles
# 3. Provide clear, data-driven recommendations with specific reasoning
# 4. Maintain a conservative approach to risk management

# Your analysis should be thorough but concise, focusing on actionable insights."""

#     analysis_prompt = f"""
#     Based on the following data, provide a detailed trading analysis:

#     MARKET DATA:
#     - Current BTC Price: {market_data['close'].iloc[-1]}
#     - 24h Price Change: {((market_data['close'].iloc[-1] - market_data['close'].iloc[-24])/market_data['close'].iloc[-24])*100}%
#     - Recent Price Trend: {market_data['close'].iloc[-24:].describe()}

#     NEWS SENTIMENT:
#     {[news_item['title'] for news_item in news[:5]]}

#     SOCIAL SENTIMENT:
#     {tweets[:5]}

#     TRADING HISTORY:
#     {trading_history}

#     Please provide your analysis in the following format:
#     1. Market Overview: Brief summary of current market conditions
#     2. Key Factors: List the most important factors influencing the decision
#     3. Risk Assessment: Evaluate potential risks and rewards
#     4. Recommendation: Choose ONE of the following:
#        - BUY: If conditions suggest a buying opportunity
#        - SELL: If conditions suggest selling is advisable
#        - HOLD: If current position should be maintained
#     5. Reasoning: Detailed explanation of your recommendation
#     6. Confidence Level: Rate your confidence in this decision (1-10)
#     """
    
#     response = openai.ChatCompletion.create(
#         model="gpt-4",
#         messages=[
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": analysis_prompt}
#         ],
#         temperature=0.7,
#         max_tokens=1000
#     )
    
#     return response.choices[0].message.content

# def execute_trade(decision, binance_client):
#     if decision.lower().startswith('buy'):
#         # Implement buy logic
#         order = binance_client.create_order(
#             symbol='BTCUSDT',
#             side=Client.SIDE_BUY,
#             type=Client.ORDER_TYPE_MARKET,
#             quantity=0.001  # Adjust based on your trading size
#         )
#         return {'action': 'buy', 'order': order}
    
#     elif decision.lower().startswith('sell'):
#         # Implement sell logic
#         order = binance_client.create_order(
#             symbol='BTCUSDT',
#             side=Client.SIDE_SELL,
#             type=Client.ORDER_TYPE_MARKET,
#             quantity=0.001  # Adjust based on your trading size
#         )
#         return {'action': 'sell', 'order': order}
    
#     return {'action': 'hold', 'order': None}

# def save_trading_history(trade_data):
#     """Save trade data to Excel file with multiple sheets"""
#     excel_file = 'trading_history.xlsx'
    
#     # Create new DataFrame with current trade
#     new_trade_df = pd.DataFrame([trade_data])
#     new_trade_df['timestamp'] = datetime.now()
    
#     try:
#         # Try to read existing Excel file
#         with pd.ExcelFile(excel_file) as xls:
#             # Read existing sheets
#             trades_df = pd.read_excel(xls, 'Trades')
#             performance_df = pd.read_excel(xls, 'Performance')
#     except FileNotFoundError:
#         # Create new DataFrames if file doesn't exist
#         trades_df = pd.DataFrame()
#         performance_df = pd.DataFrame()
    
#     # Append new trade to trades sheet
#     trades_df = pd.concat([trades_df, new_trade_df], ignore_index=True)
    
#     # Update performance metrics
#     if len(trades_df) > 1:
#         trades_df['timestamp'] = pd.to_datetime(trades_df['timestamp'])
#         trades_df = trades_df.sort_values('timestamp')
        
#         # Calculate performance metrics
#         trades_df['profit_loss'] = trades_df.apply(
#             lambda x: (x['price'] * x['quantity']) if x['action'] == 'sell' 
#             else -(x['price'] * x['quantity']), axis=1
#         )
        
#         # Create performance summary
#         performance_data = {
#             'Total Trades': len(trades_df),
#             'Buy Trades': len(trades_df[trades_df['action'] == 'buy']),
#             'Sell Trades': len(trades_df[trades_df['action'] == 'sell']),
#             'Total P/L': trades_df['profit_loss'].sum(),
#             'Average Trade P/L': trades_df['profit_loss'].mean(),
#             'Win Rate': len(trades_df[trades_df['profit_loss'] > 0]) / len(trades_df) * 100,
#             'Last Updated': datetime.now()
#         }
        
#         performance_df = pd.DataFrame([performance_data])
    
#     # Save to Excel with multiple sheets
#     with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
#         trades_df.to_excel(writer, sheet_name='Trades', index=False)
#         performance_df.to_excel(writer, sheet_name='Performance', index=False)
        
#         # Auto-adjust column widths
#         for sheet_name in writer.sheets:
#             worksheet = writer.sheets[sheet_name]
#             for idx, col in enumerate(trades_df.columns):
#                 max_length = max(
#                     trades_df[col].astype(str).apply(len).max(),
#                     len(str(col))
#                 )
#                 worksheet.column_dimensions[chr(65 + idx)].width = max_length + 2

# def load_trading_history():
#     """Load trading history from Excel file"""
#     try:
#         with pd.ExcelFile('trading_history.xlsx') as xls:
#             return pd.read_excel(xls, 'Trades')
#     except FileNotFoundError:
#         return pd.DataFrame()

# def view_trading_history():
#     """View detailed trading history with performance metrics"""
#     try:
#         with pd.ExcelFile('trading_history.xlsx') as xls:
#             trades_df = pd.read_excel(xls, 'Trades')
#             performance_df = pd.read_excel(xls, 'Performance')
#     except FileNotFoundError:
#         print("No trading history available.")
#         return
    
#     if trades_df.empty:
#         print("No trading history available.")
#         return
    
#     print("\n=== Trading History ===")
#     print(f"Total number of trades: {performance_df['Total Trades'].iloc[0]}")
#     print(f"Buy trades: {performance_df['Buy Trades'].iloc[0]}")
#     print(f"Sell trades: {performance_df['Sell Trades'].iloc[0]}")
#     print(f"Total P/L: ${performance_df['Total P/L'].iloc[0]:.2f}")
#     print(f"Average Trade P/L: ${performance_df['Average Trade P/L'].iloc[0]:.2f}")
#     print(f"Win Rate: {performance_df['Win Rate'].iloc[0]:.2f}%")
    
#     # Show recent trades
#     print("\nRecent Trades:")
#     recent_trades = trades_df.tail(5)
#     for _, trade in recent_trades.iterrows():
#         print(f"\nDate: {trade['timestamp']}")
#         print(f"Action: {trade['action'].upper()}")
#         print(f"Price: ${trade['price']:.2f}")
#         print(f"Quantity: {trade['quantity']:.4f} BTC")
#         print(f"P/L: ${trade['profit_loss']:.2f}")
#         print("-" * 50)
    
#     return trades_df

# def trading_job():
#     # Initialize clients
#     twitter_client, binance_client = initialize_clients()
    
#     # Gather data
#     news = get_deepsearch_news()
#     tweets = get_twitter_sentiment()
#     market_data = get_btc_market_data()
#     trading_history = load_trading_history()
    
#     # Analyze with GPT
#     decision = analyze_with_gpt(news, tweets, market_data, trading_history)
    
#     # Execute trade based on decision
#     trade_result = execute_trade(decision, binance_client)
    
#     # Save trading history
#     if trade_result['order']:
#         save_trading_history({
#             'action': trade_result['action'],
#             'price': float(trade_result['order']['price']),
#             'quantity': float(trade_result['order']['executedQty']),
#             'decision_reasoning': decision
#         })

# def main():
#     # Schedule the trading job to run every 8 hours
#     schedule.every(8).hours.do(trading_job)
    
#     while True:
#         schedule.run_pending()
#         time.sleep(60)

# if __name__ == "__main__":
#     main()
