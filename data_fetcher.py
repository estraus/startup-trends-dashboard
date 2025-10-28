"""Module for fetching startup data from various sources."""

import requests
import pandas as pd
from typing import List, Dict, Optional
import json
import os
from datetime import datetime


class StartupDataFetcher:
    """Fetches startup data from public sources."""

    def __init__(self):
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)

    def create_sample_data(self) -> pd.DataFrame:
        """
        Create sample startup data for demonstration.
        In production, this would fetch from real APIs.
        """
        sample_startups = [
            {
                "name": "OpenAI",
                "description": "AI research and deployment company creating safe AGI. Developed GPT models and ChatGPT.",
                "funding_total": 11300000000,
                "founded_year": 2015,
                "location": "San Francisco, CA"
            },
            {
                "name": "Stripe",
                "description": "Payment processing platform for internet businesses. Provides APIs for online payments.",
                "funding_total": 2200000000,
                "founded_year": 2010,
                "location": "San Francisco, CA"
            },
            {
                "name": "Databricks",
                "description": "Unified analytics platform built on Apache Spark for data engineering and machine learning.",
                "funding_total": 3500000000,
                "founded_year": 2013,
                "location": "San Francisco, CA"
            },
            {
                "name": "Notion",
                "description": "All-in-one workspace for notes, tasks, wikis, and databases. Productivity tool for teams.",
                "funding_total": 343000000,
                "founded_year": 2016,
                "location": "San Francisco, CA"
            },
            {
                "name": "Figma",
                "description": "Collaborative interface design tool built in the browser. Vector graphics editor and prototyping.",
                "funding_total": 332900000,
                "founded_year": 2012,
                "location": "San Francisco, CA"
            },
            {
                "name": "Hugging Face",
                "description": "Platform for building, training and deploying ML models. Focus on NLP and transformers.",
                "funding_total": 395000000,
                "founded_year": 2016,
                "location": "New York, NY"
            },
            {
                "name": "Scale AI",
                "description": "Data labeling and annotation platform for machine learning training data.",
                "funding_total": 602000000,
                "founded_year": 2016,
                "location": "San Francisco, CA"
            },
            {
                "name": "Vercel",
                "description": "Platform for frontend developers providing hosting and serverless functions. Creators of Next.js.",
                "funding_total": 313000000,
                "founded_year": 2015,
                "location": "San Francisco, CA"
            },
            {
                "name": "Anthropic",
                "description": "AI safety and research company building reliable, interpretable, and steerable AI systems.",
                "funding_total": 7300000000,
                "founded_year": 2021,
                "location": "San Francisco, CA"
            },
            {
                "name": "Tempus",
                "description": "Healthcare technology company using AI for precision medicine and cancer research.",
                "funding_total": 1300000000,
                "founded_year": 2015,
                "location": "Chicago, IL"
            },
            {
                "name": "Oscar Health",
                "description": "Technology-focused health insurance company providing user-friendly healthcare coverage.",
                "funding_total": 1600000000,
                "founded_year": 2012,
                "location": "New York, NY"
            },
            {
                "name": "Devoted Health",
                "description": "Medicare Advantage insurance company using technology to improve senior healthcare.",
                "funding_total": 1900000000,
                "founded_year": 2017,
                "location": "Waltham, MA"
            },
            {
                "name": "Rippling",
                "description": "Unified HR, IT, and Finance platform managing payroll, benefits, and employee systems.",
                "funding_total": 1200000000,
                "founded_year": 2016,
                "location": "San Francisco, CA"
            },
            {
                "name": "Linear",
                "description": "Issue tracking tool for software development teams. Focus on speed and user experience.",
                "funding_total": 52000000,
                "founded_year": 2019,
                "location": "San Francisco, CA"
            },
            {
                "name": "Replit",
                "description": "Collaborative browser-based IDE for building and deploying applications online.",
                "funding_total": 197000000,
                "founded_year": 2016,
                "location": "San Francisco, CA"
            },
            {
                "name": "Instacart",
                "description": "Grocery delivery and pickup service connecting customers with personal shoppers.",
                "funding_total": 2700000000,
                "founded_year": 2012,
                "location": "San Francisco, CA"
            },
            {
                "name": "Chime",
                "description": "Mobile-first neobank providing fee-free banking services and early direct deposit.",
                "funding_total": 2300000000,
                "founded_year": 2013,
                "location": "San Francisco, CA"
            },
            {
                "name": "Plaid",
                "description": "Financial services API enabling applications to connect with users' bank accounts.",
                "funding_total": 734000000,
                "founded_year": 2013,
                "location": "San Francisco, CA"
            },
            {
                "name": "Anduril",
                "description": "Defense technology company building autonomous systems and infrastructure for national security.",
                "funding_total": 2700000000,
                "founded_year": 2017,
                "location": "Costa Mesa, CA"
            },
            {
                "name": "Faire",
                "description": "Online wholesale marketplace connecting retailers with independent brands and makers.",
                "funding_total": 1100000000,
                "founded_year": 2017,
                "location": "San Francisco, CA"
            }
        ]

        df = pd.DataFrame(sample_startups)

        # Save to CSV
        csv_path = os.path.join(self.data_dir, "sample_startups.csv")
        df.to_csv(csv_path, index=False)
        print(f"Sample data created: {len(df)} startups saved to {csv_path}")

        return df

    def fetch_from_url(self, url: str, file_format: str = "csv") -> Optional[pd.DataFrame]:
        """
        Fetch startup data from a remote URL.

        Args:
            url: URL to fetch data from
            file_format: Format of the file ('csv', 'json', 'excel')

        Returns:
            DataFrame with startup data or None if fetch fails
        """
        try:
            print(f"Fetching data from {url}...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            if file_format == "csv":
                from io import StringIO
                df = pd.read_csv(StringIO(response.text))
            elif file_format == "json":
                data = response.json()
                df = pd.DataFrame(data)
            elif file_format == "excel":
                from io import BytesIO
                df = pd.read_excel(BytesIO(response.content))
            else:
                raise ValueError(f"Unsupported format: {file_format}")

            print(f"✓ Successfully fetched {len(df)} records from remote source")

            # Save to cache
            cache_path = os.path.join(self.data_dir, "remote_data_cache.csv")
            df.to_csv(cache_path, index=False)

            # Save metadata
            metadata = {
                "url": url,
                "last_fetched": datetime.now().isoformat(),
                "record_count": len(df)
            }
            metadata_path = os.path.join(self.data_dir, "remote_data_metadata.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)

            return df

        except Exception as e:
            print(f"✗ Error fetching data from URL: {e}")
            return None

    def fetch_yc_companies(self, limit: int = 50) -> pd.DataFrame:
        """
        Fetch Y Combinator companies from their public directory.
        Note: This is a simplified version. Real implementation would need proper web scraping.
        """
        print("Note: YC scraping requires proper implementation. Using sample data instead.")
        return self.create_sample_data()

    def load_from_csv_url(self, csv_url: str, use_cache: bool = True) -> pd.DataFrame:
        """
        Load data from a remote CSV URL with caching support.

        Args:
            csv_url: URL of the CSV file
            use_cache: Whether to use cached data if available

        Returns:
            DataFrame with startup data
        """
        cache_path = os.path.join(self.data_dir, "remote_data_cache.csv")
        metadata_path = os.path.join(self.data_dir, "remote_data_metadata.json")

        # Check if we should use cache
        if use_cache and os.path.exists(cache_path) and os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)

            if metadata.get('url') == csv_url:
                print(f"Using cached data from {metadata.get('last_fetched')}")
                return pd.read_csv(cache_path)

        # Fetch fresh data
        df = self.fetch_from_url(csv_url, file_format="csv")

        if df is None:
            # Fall back to cache if available
            if os.path.exists(cache_path):
                print("Falling back to cached data...")
                return pd.read_csv(cache_path)
            else:
                print("No cache available. Using sample data.")
                return self.create_sample_data()

        return df

    def load_data(self, source: str = "local", url: Optional[str] = None) -> pd.DataFrame:
        """
        Load startup data from various sources.

        Args:
            source: Data source ('local', 'url', 'sample')
            url: URL to fetch data from (required if source='url')

        Returns:
            DataFrame with startup data
        """
        if source == "url":
            if not url:
                raise ValueError("URL must be provided when source='url'")
            return self.load_from_csv_url(url)
        elif source == "sample":
            return self.create_sample_data()
        else:  # local
            csv_path = os.path.join(self.data_dir, "sample_startups.csv")

            if os.path.exists(csv_path):
                print(f"Loading existing data from {csv_path}")
                return pd.read_csv(csv_path)
            else:
                print("Creating new sample data...")
                return self.create_sample_data()


if __name__ == "__main__":
    fetcher = StartupDataFetcher()
    df = fetcher.load_data()
    print(f"\nLoaded {len(df)} startups")
    print(df.head())
