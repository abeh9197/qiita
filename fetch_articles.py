import os
import requests
from datetime import datetime
from dotenv import load_dotenv
import csv
from log import logger


load_dotenv()

API_TOKEN = os.getenv('QIITA_API_TOKEN')

if not API_TOKEN:
    raise ValueError("Qiita API Token is missing. Please set it in the .env file.")

headers = {
    'Authorization': f'Bearer {API_TOKEN}'
}

def fetch_qiita_articles(page: int = 1, per_page: int = 100):
    url = f'https://qiita.com/api/v2/items?query=created:>=2024-02-01 created:<=2024-02-28 stocks:>=100'
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Error fetching data from Qiita API: {response.status_code} {response.text}")

    return response.json()

def filter_articles(articles: list):
    filtered = []
    for article in articles:
        created_at = datetime.strptime(article['created_at'], '%Y-%m-%dT%H:%M:%S%z')
        if created_at.year == 2024 and article['likes_count'] >= 1:
            filtered.append({
                'title': article['title'],
                'likes_count': article['likes_count'],
                'created_at': article['created_at']
            })
    return filtered

def get_qiita_articles():
    logger.info("Fetch articles...")
    page = 1
    articles = []

    while True:
        data = fetch_qiita_articles(page)
        filtered_articles = filter_articles(data)
        articles.extend(filtered_articles)

        if len(data) < 100:
            break
        page += 1

    return articles

def export_to_csv(articles, filename="qiita_articles.csv"):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['title', 'likes_count', 'created_at'])
        writer.writeheader()
        writer.writerows(articles)

if __name__ == "__main__":
    try:
        articles = get_qiita_articles()
        if articles:
            export_to_csv(articles)
            logger.info(f"Exported {len(articles)} articles to qiita_articles.csv")
        else:
            logger.info("No articles found that match the criteria.")
    except Exception as e:
        logger.info(f"An error occurred: {e}")
