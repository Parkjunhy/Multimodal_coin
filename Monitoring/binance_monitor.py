import os
import logging
import pandas as pd
from binance.client import Client
from binance.exceptions import BinanceAPIException
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

class BinanceMonitor:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Get API credentials
        self.api_key = os.getenv('BINANCE_API_KEY')
        self.api_secret = os.getenv('BINANCE_SECRET_KEY')
        
        if not self.api_key or not self.api_secret:
            logger.error("Binance API credentials not found in environment variables")
            raise ValueError("Please set BINANCE_API_KEY and BINANCE_SECRET_KEY in .env file")
        
        try:
            # Initialize Binance client
            self.client = Client(self.api_key, self.api_secret)
            
            # Test connection
            self._test_connection()
            logger.info("Successfully initialized Binance client")
            
        except BinanceAPIException as e:
            logger.error(f"Binance API Error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Binance client: {str(e)}")
            raise
            
    def _test_connection(self):
        """Test the API connection"""
        try:
            # Get server time to test connection
            server_time = self.client.get_server_time()
            logger.info("Binance API connection test successful")
            return True
        except Exception as e:
            logger.error(f"Binance API connection test failed: {str(e)}")
            raise
            
    def get_btc_price(self) -> dict:
        """Get current BTC price and 24h stats"""
        try:
            # Get BTC ticker
            ticker = self.client.get_ticker(symbol='BTCUSDT')
            
            price_data = {
                'symbol': 'BTCUSDT',
                'price': float(ticker['lastPrice']),
                'price_change': float(ticker['priceChange']),
                'price_change_percent': float(ticker['priceChangePercent']),
                'high_24h': float(ticker['highPrice']),
                'low_24h': float(ticker['lowPrice']),
                'volume': float(ticker['volume']),
                'timestamp': datetime.fromtimestamp(ticker['closeTime'] / 1000)
            }
            
            logger.info(f"Successfully fetched BTC price: ${price_data['price']:,.2f}")
            return price_data
            
        except BinanceAPIException as e:
            logger.error(f"Binance API Error in get_btc_price: {str(e)}")
            return {}
        except Exception as e:
            logger.error(f"Error fetching BTC price: {str(e)}")
            return {}
            
    def get_recent_trades(self, symbol: str = 'BTCUSDT', limit: int = 50) -> pd.DataFrame:
        """Get recent trades for a symbol"""
        try:
            trades = self.client.get_recent_trades(symbol=symbol, limit=limit)
            
            df = pd.DataFrame(trades)
            df['time'] = pd.to_datetime(df['time'], unit='ms')
            df['price'] = df['price'].astype(float)
            df['qty'] = df['qty'].astype(float)
            
            logger.info(f"Successfully fetched {len(df)} recent trades for {symbol}")
            return df
            
        except BinanceAPIException as e:
            logger.error(f"Binance API Error in get_recent_trades: {str(e)}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error fetching recent trades: {str(e)}")
            return pd.DataFrame()
            
    def get_order_book(self, symbol: str = 'BTCUSDT', limit: int = 10) -> dict:
        """Get current order book"""
        try:
            depth = self.client.get_order_book(symbol=symbol, limit=limit)
            
            # Process order book data
            order_book = {
                'bids': [{'price': float(bid[0]), 'quantity': float(bid[1])} for bid in depth['bids']],
                'asks': [{'price': float(ask[0]), 'quantity': float(ask[1])} for ask in depth['asks']]
            }
            
            logger.info(f"Successfully fetched order book for {symbol}")
            return order_book
            
        except BinanceAPIException as e:
            logger.error(f"Binance API Error in get_order_book: {str(e)}")
            return {}
        except Exception as e:
            logger.error(f"Error fetching order book: {str(e)}")
            return {}

def main():
    try:
        logger.info("Starting Binance Monitor")
        monitor = BinanceMonitor()
        
        # Get BTC price
        btc_price = monitor.get_btc_price()
        if btc_price:
            print("\nBTC Price Information:")
            print("=====================")
            print(f"Current Price: ${btc_price['price']:,.2f}")
            print(f"24h Change: {btc_price['price_change_percent']}%")
            print(f"24h High: ${btc_price['high_24h']:,.2f}")
            print(f"24h Low: ${btc_price['low_24h']:,.2f}")
            print(f"24h Volume: {btc_price['volume']:,.2f} BTC")
            
        # Get recent trades
        trades_df = monitor.get_recent_trades(limit=5)
        if not trades_df.empty:
            print("\nRecent Trades:")
            print("==============")
            for _, trade in trades_df.iterrows():
                print(f"Time: {trade['time']}")
                print(f"Price: ${float(trade['price']):,.2f}")
                print(f"Quantity: {float(trade['qty']):,.8f} BTC")
                print("-" * 40)
                
        # Get order book
        order_book = monitor.get_order_book(limit=5)
        if order_book:
            print("\nOrder Book:")
            print("===========")
            print("Top 5 Bids:")
            for bid in order_book['bids']:
                print(f"${bid['price']:,.2f} - {bid['quantity']:,.8f} BTC")
            print("\nTop 5 Asks:")
            for ask in order_book['asks']:
                print(f"${ask['price']:,.2f} - {ask['quantity']:,.8f} BTC")
                
    except Exception as e:
        logger.error(f"Main function error: {str(e)}")
        logger.error("Please check your .env file contains the correct Binance API credentials")
        raise

if __name__ == "__main__":
    main() 