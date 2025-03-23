import os
import logging
import json
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Dict, List

# 환경 변수 로드 (최상단에서 실행)
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
)
logger = logging.getLogger(__name__)

class GeminiMonitor:
    def __init__(self):
        # 환경 변수에서 API 키 가져오기
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.error("Gemini API key not found in environment variables")
            raise ValueError("Please set GEMINI_API_KEY in .env file")
        
        try:
            # Gemini API 설정
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-1.5-pro")
            logger.info("Successfully initialized Gemini AI")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI: {str(e)}")
            raise

    def analyze_crypto_sentiment(self, text: str) -> Dict:
        """
        암호화폐 관련 뉴스나 텍스트를 분석하여 감정(sentiment) 및 주요 포인트를 반환
        """
        try:
            prompt = f"""
            Analyze the following cryptocurrency-related text and provide:
            1. Overall sentiment (bullish/bearish/neutral)
            2. Key points or insights
            3. Potential market impact
            4. Confidence level in the analysis (0-100%)

            Text to analyze:
            {text}

            Format the response as JSON:
            {{
                "sentiment": "bullish/bearish/neutral",
                "key_points": ["point1", "point2"],
                "market_impact": "high/medium/low",
                "confidence": 85
            }}
            """
            response = self.model.generate_content(prompt)

            # 응답이 JSON 형식인지 확인 후 변환
            try:
                analysis = json.loads(response.text)
                logger.info(f"Sentiment analysis successful: {analysis}")
                return analysis
            except json.JSONDecodeError:
                logger.warning("API response is not in JSON format. Returning raw text.")
                return {
                    "sentiment": "unknown",
                    "key_points": [response.text],
                    "market_impact": "unclear",
                    "confidence": 0
                }
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}")
            return {}

    def get_crypto_insights(self, topic: str) -> Dict:
        """
        특정 암호화폐 주제에 대한 AI 기반 인사이트 제공
        """
        try:
            prompt = f"""
            Provide detailed analysis and insights about the following cryptocurrency topic:
            {topic}

            Include:
            1. Current state/explanation
            2. Potential implications
            3. Related factors to consider
            4. Future outlook

            Format the response as JSON:
            {{
                "current_state": "Description of current state",
                "implications": ["implication1", "implication2"],
                "related_factors": ["factor1", "factor2"],
                "outlook": "positive/negative/uncertain"
            }}
            """
            response = self.model.generate_content(prompt)

            # JSON 변환 시도
            try:
                insights = json.loads(response.text)
                logger.info(f"Generated insights for topic: {topic}")
                return insights
            except json.JSONDecodeError:
                logger.warning("API response is not in JSON format. Returning raw text.")
                return {
                    "current_state": response.text,
                    "implications": [],
                    "related_factors": [],
                    "outlook": "unclear"
                }
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            return {}

def main():
    try:
        logger.info("Starting Gemini AI Monitor")
        monitor = GeminiMonitor()

        # 테스트: 뉴스 감성 분석
        news_text = """
        Bitcoin surges to new highs as institutional adoption increases.
        Major banks are now offering crypto custody services, and ETF
        applications are gaining traction with regulators.
        """
        sentiment = monitor.analyze_crypto_sentiment(news_text)
        if sentiment:
            print("\n🔹 Sentiment Analysis:")
            print("=====================")
            print(f"📈 Sentiment: {sentiment.get('sentiment', 'N/A')}")
            print(f"🔍 Confidence: {sentiment.get('confidence', 0)}%")
            print("\n📝 Key Points:")
            for point in sentiment.get("key_points", []):
                print(f"- {point}")
            print(f"\n📊 Market Impact: {sentiment.get('market_impact', 'N/A')}")

        # 테스트: 암호화폐 인사이트 분석
        topic = "Bitcoin ETF approval impact on crypto market"
        insights = monitor.get_crypto_insights(topic)
        if insights:
            print("\n🔹 Crypto Insights:")
            print("===================")
            print(f"📌 Current State: {insights.get('current_state', 'N/A')}")
            print("\n🔍 Implications:")
            for imp in insights.get("implications", []):
                print(f"- {imp}")
            print("\n📊 Outlook:", insights.get("outlook", "N/A"))

    except Exception as e:
        logger.error(f"Main function error: {str(e)}")
        logger.error("Please check your .env file contains the correct Gemini API key")
        raise

if __name__ == "__main__":
    main()
