# tasks/social_media.py
from celery import shared_task
import tweepy
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import os
from sqlalchemy.orm import Session
from database import SessionLocal
from models import HazardReport
import re

# Twitter API credentials (should be in environment variables)
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

@shared_task
def scrape_twitter_for_hazards(keywords=None, location=None, max_results=100):
    """Scrape Twitter for hazard-related posts"""
    if not keywords:
        keywords = [
            "tsunami", "storm", "flood", "high waves", "coastal erosion",
            "cyclone", "typhoon", "hurricane", "tidal surge", "ocean hazard",
            "marine warning", "coastal flood", "beach erosion"
        ]
    
    try:
        client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)
        
        # Build query
        query = " OR ".join([f'"{keyword}"' for keyword in keywords])
        if location:
            query += f" place:{location}"
        
        # Search recent tweets
        tweets = client.search_recent_tweets(
            query=query,
            max_results=min(max_results, 100),
            tweet_fields=["created_at", "author_id", "geo", "public_metrics"],
            expansions=["author_id", "geo.place_id"],
            user_fields=["name", "username", "location"],
            place_fields=["full_name", "country", "geo"]
        )
        
        results = []
        if tweets.data:
            for tweet in tweets.data:
                result = {
                    "id": tweet.id,
                    "text": tweet.text,
                    "created_at": tweet.created_at.isoformat(),
                    "author_id": tweet.author_id,
                    "retweet_count": tweet.public_metrics.get("retweet_count", 0),
                    "like_count": tweet.public_metrics.get("like_count", 0),
                    "reply_count": tweet.public_metrics.get("reply_count", 0),
                    "source": "twitter"
                }
                
                # Try to extract location
                if hasattr(tweet, 'geo') and tweet.geo:
                    result["location"] = tweet.geo.get("place_id")
                
                results.append(result)
        
        return results
        
    except Exception as e:
        print(f"Twitter scraping error: {e}")
        return []

@shared_task
def scrape_news_sites():
    """Scrape news websites for hazard reports"""
    news_sources = [
        "https://incois.gov.in",
        "https://mausam.imd.gov.in",
        "https://ndma.gov.in",
        # Add more relevant news sources
    ]
    
    results = []
    for url in news_sources:
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for hazard-related content (this would need customization per site)
            articles = soup.find_all(['article', 'div'], class_=re.compile(r'(news|article|alert|warning)', re.I))
            
            for article in articles[:5]:  # Limit to 5 articles per site
                title_elem = article.find(['h1', 'h2', 'h3', 'h4'])
                content_elem = article.find('p') or article
                
                if title_elem and content_elem:
                    result = {
                        "title": title_elem.get_text().strip(),
                        "content": content_elem.get_text().strip()[:500],
                        "url": url,
                        "source": "news",
                        "scraped_at": datetime.utcnow().isoformat()
                    }
                    results.append(result)
                    
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            continue
    
    return results

@shared_task
def monitor_social_media_continuously():
    """Continuous monitoring task (to be scheduled)"""
    twitter_results = scrape_twitter_for_hazards.delay()
    news_results = scrape_news_sites.delay()
    
    return {
        "twitter": twitter_results.get() if twitter_results.ready() else [],
        "news": news_results.get() if news_results.ready() else []
    }

@shared_task
def process_social_media_data(raw_data):
    """Process and analyze social media data"""
    processed_data = []
    
    for item in raw_data:
        # Basic NLP processing
        text = item.get('text', '') or item.get('content', '')
        
        # Simple keyword analysis
        hazard_keywords = {
            'tsunami': 0, 'storm': 0, 'flood': 0, 'wave': 0, 
            'erosion': 0, 'cyclone': 0, 'warning': 0, 'alert': 0
        }
        
        for keyword in hazard_keywords:
            hazard_keywords[keyword] = text.lower().count(keyword)
        
        # Calculate urgency score
        urgency_score = sum(hazard_keywords.values())
        
        processed_item = {
            **item,
            "hazard_keywords": hazard_keywords,
            "urgency_score": urgency_score,
            "processed_at": datetime.utcnow().isoformat()
        }
        
        processed_data.append(processed_item)
    
    return processed_data
