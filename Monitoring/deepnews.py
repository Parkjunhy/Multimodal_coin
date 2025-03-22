import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Set up logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DeepSearchNews:
    def __init__(self):
        self.base_url = "https://api-v2.deepsearch.com/v1"
        self.api_key = "ecd808ea2978405cac570bd27531a24a"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        logger.info(f"Initialized DeepSearchNews with base URL: {self.base_url}")
    
    def get_btc_news(self, days_ago: int = 1) -> Dict:
        """
        Fetch Bitcoin related news from DeepSearch API
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_ago)
            
            # Using the correct endpoint
            endpoint = f"{self.base_url}/global-articles"
            
            # Query parameters
            params = {
                'q': 'bitcoin OR BTC OR cryptocurrency',
                'from': start_date.strftime('%Y-%m-%d'),
                'to': end_date.strftime('%Y-%m-%d'),
                'lang': 'en',
                'sort': 'date',
                'order': 'desc',
                'api_key': self.api_key  # Including API key in params as well
            }
            
            logger.info(f"Making request to endpoint: {endpoint}")
            logger.info(f"With parameters: {params}")
            
            response = self.session.get(endpoint, params=params)
            
            # Log response details
            logger.info(f"Response status code: {response.status_code}")
            
            try:
                response_text = response.text
                logger.info(f"Response content preview: {response_text[:500]}...")
            except Exception as e:
                logger.warning(f"Could not log response content: {str(e)}")
            
            response.raise_for_status()
            
            try:
                data = response.json()
                logger.info("Successfully parsed JSON response")
                return data
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON: {str(e)}")
                return {"error": "Invalid JSON response"}
            
        except requests.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            logger.error(error_msg)
            try:
                error_detail = response.text if response else "No response"
                logger.error(f"Error detail: {error_detail}")
            except:
                pass
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def parse_news_data(self, news_data: Dict) -> List[Dict]:
        """
        Parse and clean the news data
        """
        cleaned_articles = []
        
        if 'error' in news_data:
            logger.error(f"Error in news data: {news_data['error']}")
            return cleaned_articles
        
        # Try different possible response structures
        articles = news_data.get('articles') or news_data.get('data') or news_data.get('results') or []
        
        if not articles:
            logger.warning("No articles found in response")
            logger.info(f"Available keys in response: {list(news_data.keys())}")
            return cleaned_articles
            
        for article in articles:
            try:
                cleaned_article = {
                    'title': article.get('title', ''),
                    'published_at': article.get('publishedAt') or article.get('published_at') or article.get('date', ''),
                    'source': article.get('source', {}).get('name') or article.get('source', ''),
                    'url': article.get('url') or article.get('link', ''),
                    'description': article.get('description') or article.get('summary', '')
                }
                if any(cleaned_article.values()):  # Only add if at least one field has data
                    cleaned_articles.append(cleaned_article)
            except Exception as e:
                logger.error(f"Error parsing article: {str(e)}")
                continue
            
        return cleaned_articles

def main():
    try:
        logger.info("Starting news fetching process")
        news_client = DeepSearchNews()
        
        btc_news = news_client.get_btc_news(days_ago=3)
        
        if 'error' in btc_news:
            logger.error(f"Error occurred while fetching news: {btc_news['error']}")
            return
        
        cleaned_news = news_client.parse_news_data(btc_news)
        
        if not cleaned_news:
            logger.warning("No news articles were found or parsed successfully")
            return
            
        print("\nRecent Bitcoin News:")
        print("===================")
        
        for idx, article in enumerate(cleaned_news, 1):
            print(f"\n{idx}. {article['title']}")
            print(f"Published: {article['published_at']}")
            print(f"Source: {article['source']}")
            print(f"URL: {article['url']}")
            print(f"Description: {article['description']}")
            print("-" * 80)
            
    except Exception as e:
        logger.error(f"Main function error: {str(e)}")

if __name__ == "__main__":
    main()
