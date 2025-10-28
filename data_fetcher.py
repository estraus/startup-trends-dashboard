"""Module for fetching startup data from various sources."""

import requests
import pandas as pd
from typing import List, Dict
import json
import os


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

    def fetch_yc_companies(self, limit: int = 50) -> pd.DataFrame:
        """
        Fetch Y Combinator companies from their public directory.
        Note: This is a simplified version. Real implementation would need proper web scraping.
        """
        print("Note: YC scraping requires proper implementation. Using sample data instead.")
        return self.create_sample_data()

    def load_data(self) -> pd.DataFrame:
        """Load startup data from CSV if exists, otherwise create sample data."""
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
