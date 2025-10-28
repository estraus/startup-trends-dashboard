"""Fetch new startup launches from Product Hunt."""

import requests
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json
import os
import time


class ProductHuntFetcher:
    """Fetch new product launches from Product Hunt."""

    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize Product Hunt fetcher.

        Args:
            api_token: Optional Product Hunt API token
        """
        self.base_url = "https://api.producthunt.com/v2/api/graphql"
        self.api_token = api_token
        self.cache_dir = "data/cache"
        os.makedirs(self.cache_dir, exist_ok=True)

    def fetch_recent_launches(self, days_back: int = 30, limit: int = 50) -> pd.DataFrame:
        """
        Fetch recent product launches from Product Hunt.

        Note: This is a simplified version. Full implementation requires OAuth.
        For now, we'll create a structure that can be populated manually or
        via web scraping.

        Args:
            days_back: How many days back to look
            limit: Maximum number of products

        Returns:
            DataFrame with product launch data
        """
        print(f"Fetching Product Hunt launches (last {days_back} days)...")

        # Since PH API requires OAuth setup, we'll provide a framework
        # that users can populate manually or via scraping

        print("Note: Full Product Hunt integration requires API token.")
        print("You can:")
        print("  1. Get API access at: https://api.producthunt.com/v2/docs")
        print("  2. Manually scrape from: https://www.producthunt.com/")
        print("  3. Use the import_from_csv() method to load PH data\n")

        # Return empty DataFrame with proper structure
        return pd.DataFrame(columns=[
            "name",
            "tagline",
            "description",
            "website",
            "launch_date",
            "upvotes",
            "comments",
            "topics",
            "maker",
            "featured"
        ])

    def import_from_csv(self, csv_path: str) -> pd.DataFrame:
        """
        Import Product Hunt data from CSV file.

        CSV should have columns:
        - name: Product name
        - tagline: Short description
        - description: Full description
        - website: Product website
        - launch_date: Launch date (YYYY-MM-DD)
        - upvotes: Number of upvotes
        - comments: Number of comments
        - topics: Comma-separated topics
        - maker: Maker/founder name

        Args:
            csv_path: Path to CSV file

        Returns:
            DataFrame with product data
        """
        print(f"Importing Product Hunt data from {csv_path}...")

        try:
            df = pd.read_csv(csv_path)
            print(f"✓ Imported {len(df)} products")
            return df
        except Exception as e:
            print(f"✗ Error importing CSV: {e}")
            return pd.DataFrame()

    def create_sample_ph_data(self) -> pd.DataFrame:
        """Create sample Product Hunt data for demonstration."""
        sample_products = [
            {
                "name": "Cursor AI",
                "tagline": "AI-first code editor",
                "description": "The AI-first code editor built to make you extraordinarily productive.",
                "website": "https://cursor.sh",
                "launch_date": "2024-01-15",
                "upvotes": 2500,
                "comments": 180,
                "topics": "developer tools, ai, coding",
                "maker": "Cursor Team",
                "featured": True
            },
            {
                "name": "v0 by Vercel",
                "tagline": "Generate UI with AI",
                "description": "A generative user interface system by Vercel powered by AI.",
                "website": "https://v0.dev",
                "launch_date": "2023-10-15",
                "upvotes": 3200,
                "comments": 250,
                "topics": "ai, developer tools, design",
                "maker": "Vercel",
                "featured": True
            },
            {
                "name": "Supermaven",
                "tagline": "Fastest AI code completion",
                "description": "Lightning-fast AI code completion with a 300,000 token context window.",
                "website": "https://supermaven.com",
                "launch_date": "2024-02-01",
                "upvotes": 1800,
                "comments": 120,
                "topics": "ai, developer tools, productivity",
                "maker": "Jacob Jackson",
                "featured": True
            },
            {
                "name": "Pika 1.0",
                "tagline": "Idea-to-video platform",
                "description": "The idea-to-video platform that brings your creativity to motion.",
                "website": "https://pika.art",
                "launch_date": "2023-11-28",
                "upvotes": 4100,
                "comments": 320,
                "topics": "ai, video, creativity",
                "maker": "Pika Labs",
                "featured": True
            },
            {
                "name": "Perplexity Pages",
                "tagline": "Turn research into beautiful content",
                "description": "Convert your Perplexity research into visually stunning, shareable pages.",
                "website": "https://perplexity.ai",
                "launch_date": "2024-03-10",
                "upvotes": 2200,
                "comments": 145,
                "topics": "ai, research, content",
                "maker": "Perplexity AI",
                "featured": True
            }
        ]

        df = pd.DataFrame(sample_products)
        print(f"Created {len(df)} sample Product Hunt entries")
        return df

    def calculate_engagement_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate engagement metrics for products.

        Args:
            df: DataFrame with product data

        Returns:
            DataFrame with engagement scores
        """
        if df.empty:
            return df

        # Calculate engagement score
        df["engagement_score"] = df["upvotes"] * 1.0 + df["comments"] * 2.0

        # Calculate days since launch
        df["launch_date"] = pd.to_datetime(df["launch_date"])
        df["days_since_launch"] = (datetime.now() - df["launch_date"]).dt.days

        # Calculate daily upvote rate
        df["upvotes_per_day"] = df["upvotes"] / df["days_since_launch"].replace(0, 1)

        return df

    def save_to_cache(self, df: pd.DataFrame, filename: str = "producthunt_products.csv"):
        """Save data to cache."""
        cache_path = os.path.join(self.cache_dir, filename)
        df.to_csv(cache_path, index=False)

        # Save metadata
        metadata = {
            "last_updated": datetime.now().isoformat(),
            "record_count": len(df),
            "source": "Product Hunt"
        }
        metadata_path = os.path.join(self.cache_dir, f"{filename}.meta.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"✓ Cached data to {cache_path}")

    def load_from_cache(self, filename: str = "producthunt_products.csv",
                       max_age_hours: int = 24) -> Optional[pd.DataFrame]:
        """Load data from cache if it exists and is recent."""
        cache_path = os.path.join(self.cache_dir, filename)
        metadata_path = os.path.join(self.cache_dir, f"{filename}.meta.json")

        if not os.path.exists(cache_path):
            return None

        # Check metadata
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)

            last_updated = datetime.fromisoformat(metadata["last_updated"])
            age_hours = (datetime.now() - last_updated).total_seconds() / 3600

            if age_hours <= max_age_hours:
                print(f"Loading cached Product Hunt data (age: {age_hours:.1f} hours)")
                return pd.read_csv(cache_path)
            else:
                print(f"Cache expired (age: {age_hours:.1f} hours > {max_age_hours} hours)")

        return None


if __name__ == "__main__":
    # Test the Product Hunt fetcher
    fetcher = ProductHuntFetcher()

    # Try to load from cache first
    df = fetcher.load_from_cache(max_age_hours=24)

    if df is None or df.empty:
        # Create sample data for demonstration
        df = fetcher.create_sample_ph_data()

        if not df.empty:
            # Calculate engagement metrics
            df = fetcher.calculate_engagement_score(df)

            # Save to cache
            fetcher.save_to_cache(df)

    # Display results
    if not df.empty:
        print("\n" + "="*80)
        print("RECENT PRODUCT HUNT LAUNCHES")
        print("="*80)
        print(df[["name", "tagline", "upvotes", "comments", "launch_date"]].to_string())
    else:
        print("No Product Hunt data available.")
