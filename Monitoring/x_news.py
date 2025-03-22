import tweepy
import os
import pandas as pd
import logging
import time
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class XNewsMonitor:
    def __init__(self):
        load_dotenv()
        self.bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        if not self.bearer_token:
            raise ValueError("Twitter Bearer Token not found in environment variables")
        
        try:
            self.client = tweepy.Client(bearer_token=self.bearer_token)
            logger.info("Successfully initialized Twitter API client")
        except Exception as e:
            logger.error(f"Failed to initialize Twitter client: {str(e)}")
            raise

    def search_crypto_news(self, hours_ago: int = 6, max_results: int = 20) -> pd.DataFrame:
        try:
            news_accounts = [
                'CoinDesk', 'Cointelegraph', 'TheBlock__', 'BitcoinMagazine', 'DocumentingBTC'
            ]
            query_parts = [
                '(bitcoin OR ethereum OR crypto OR altcoin)',
                'has:links',  # Ensures tweets contain links
                'is:verified', '-is:retweet', '-is:reply',
                f'(from:{" OR from:".join(news_accounts)})'
            ]
            query = ' '.join(query_parts)
            
            logger.info(f"Searching tweets with query: {query}")
            tweets = self.client.search_recent_tweets(
                query=query,
                tweet_fields=['created_at', 'author_id', 'public_metrics', 'entities'],
                user_fields=['name', 'username', 'verified'],
                expansions=['author_id'],
                max_results=max_results
            )
            
            if not tweets.data:
                logger.info("No tweets found matching the criteria")
                return pd.DataFrame()
            
            users = {user.id: user for user in tweets.includes['users']} if 'users' in tweets.includes else {}
            data = []
            for tweet in tweets.data:
                user = users.get(tweet.author_id, None)
                if user:
                    urls = [url['expanded_url'] for url in tweet.entities['urls']] if hasattr(tweet, 'entities') and 'urls' in tweet.entities else []
                    tweet_data = {
                        'created_at': tweet.created_at,
                        'author_name': user.name,
                        'author_username': user.username,
                        'text': tweet.text,
                        'urls': urls,
                        'likes': tweet.public_metrics.get('like_count', 0),
                        'retweets': tweet.public_metrics.get('retweet_count', 0),
                        'replies': tweet.public_metrics.get('reply_count', 0)
                    }
                    data.append(tweet_data)
            
            df = pd.DataFrame(data)
            logger.info(f"Successfully fetched {len(df)} tweets")
            return df
        
        except tweepy.TweepyException as e:
            logger.error(f"Twitter API error: {str(e)}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Unexpected error in search_crypto_news: {str(e)}")
            return pd.DataFrame()


def search_with_retry(monitor, retries=3, wait_time=60):
    for attempt in range(retries):
        df = monitor.search_crypto_news(hours_ago=6, max_results=20)
        if not df.empty:
            return df
        logger.warning(f"No results, retrying in {wait_time} seconds... ({attempt+1}/{retries})")
        time.sleep(wait_time)
    return pd.DataFrame()


def main():
    try:
        logger.info("Starting X News Monitor")
        monitor = XNewsMonitor()
        
        logger.info("Fetching crypto news with retry logic...")
        df = search_with_retry(monitor)
        
        if df.empty:
            print("No relevant crypto news found")
            return
        
        print("\nRecent Crypto News from X:")
        print("==========================")
        for idx, row in df.iterrows():
            print(f"\n{idx + 1}. @{row['author_username']} ({row['author_name']})")
            print(f"Time: {row['created_at']}")
            print(f"Tweet: {row['text']}")
            if row['urls']:
                print("Links:", ", ".join(row['urls']))
            print(f"Metrics: {row['likes']} likes, {row['retweets']} retweets, {row['replies']} replies")
            print("-" * 80)
        
    except Exception as e:
        logger.error(f"Main function error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
