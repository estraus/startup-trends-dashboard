"""Hybrid data aggregator combining GitHub, Product Hunt, and manual enrichment."""

import pandas as pd
from typing import Optional, Dict, List
from datetime import datetime
import os
import json

from github_fetcher import GitHubStartupFetcher
from producthunt_fetcher import ProductHuntFetcher


class HybridStartupFetcher:
    """
    Combines multiple data sources to create a comprehensive startup dataset.

    Data Sources:
    1. GitHub: Technical momentum (stars, forks, commits)
    2. Product Hunt: Launch visibility and community engagement
    3. Manual Enrichment: Funding data from Crunchbase (manual lookups)
    """

    def __init__(self, github_token: Optional[str] = None, ph_token: Optional[str] = None):
        """Initialize hybrid fetcher with optional API tokens."""
        self.github_fetcher = GitHubStartupFetcher(github_token)
        self.ph_fetcher = ProductHuntFetcher(ph_token)
        self.cache_dir = "data/cache"
        os.makedirs(self.cache_dir, exist_ok=True)

    def fetch_all_sources(self,
                         use_github: bool = True,
                         use_producthunt: bool = True,
                         use_cache: bool = True,
                         cache_max_age_hours: int = 24) -> Dict[str, pd.DataFrame]:
        """
        Fetch data from all available sources.

        Args:
            use_github: Whether to fetch GitHub data
            use_producthunt: Whether to fetch Product Hunt data
            use_cache: Whether to use cached data
            cache_max_age_hours: Maximum age of cache in hours

        Returns:
            Dictionary with DataFrames from each source
        """
        results = {}

        # Fetch GitHub data
        if use_github:
            print("\n" + "="*80)
            print("FETCHING GITHUB DATA")
            print("="*80)

            if use_cache:
                github_df = self.github_fetcher.load_from_cache(max_age_hours=cache_max_age_hours)
            else:
                github_df = None

            if github_df is None or github_df.empty:
                github_df = self.github_fetcher.get_trending_startups(
                    topics=["startup", "saas", "ai-startup", "fintech", "productivity"],
                    min_stars=50,
                    days_back=180,
                    limit=40
                )

                if not github_df.empty:
                    github_df = self.github_fetcher.calculate_growth_metrics(github_df)
                    self.github_fetcher.save_to_cache(github_df)

            results["github"] = github_df

        # Fetch Product Hunt data
        if use_producthunt:
            print("\n" + "="*80)
            print("FETCHING PRODUCT HUNT DATA")
            print("="*80)

            if use_cache:
                ph_df = self.ph_fetcher.load_from_cache(max_age_hours=cache_max_age_hours)
            else:
                ph_df = None

            if ph_df is None or ph_df.empty:
                # Use sample data for now
                ph_df = self.ph_fetcher.create_sample_ph_data()

                if not ph_df.empty:
                    ph_df = self.ph_fetcher.calculate_engagement_score(ph_df)
                    self.ph_fetcher.save_to_cache(ph_df)

            results["producthunt"] = ph_df

        return results

    def merge_datasets(self, github_df: pd.DataFrame, ph_df: pd.DataFrame) -> pd.DataFrame:
        """
        Merge GitHub and Product Hunt datasets intelligently.

        Args:
            github_df: GitHub startup data
            ph_df: Product Hunt data

        Returns:
            Merged DataFrame with combined insights
        """
        print("\n" + "="*80)
        print("MERGING DATASETS")
        print("="*80)

        all_startups = []

        # Process GitHub startups
        if not github_df.empty:
            for _, row in github_df.iterrows():
                startup = {
                    "name": row["name"],
                    "description": row.get("description", ""),
                    "source": "GitHub",
                    "github_url": row.get("github_url", ""),
                    "website": row.get("homepage", ""),
                    "github_stars": row.get("stars", 0),
                    "github_forks": row.get("forks", 0),
                    "star_velocity": row.get("star_velocity", 0),
                    "momentum_score": row.get("momentum_score", 0),
                    "language": row.get("language", ""),
                    "topics": row.get("topics", ""),
                    "founded_year": pd.to_datetime(row.get("created_at", "")).year if pd.notnull(row.get("created_at")) else None,
                    "funding_total": 0,  # To be manually enriched
                    "location": row.get("location", ""),
                }
                all_startups.append(startup)

        # Process Product Hunt launches
        if not ph_df.empty:
            for _, row in ph_df.iterrows():
                # Check if already exists from GitHub
                existing = next((s for s in all_startups if s["name"].lower() == row["name"].lower()), None)

                if existing:
                    # Merge with existing entry
                    existing["ph_upvotes"] = row.get("upvotes", 0)
                    existing["ph_comments"] = row.get("comments", 0)
                    existing["launch_date"] = row.get("launch_date", "")
                    if not existing["website"]:
                        existing["website"] = row.get("website", "")
                    if not existing["description"]:
                        existing["description"] = row.get("tagline", "")
                else:
                    # Add as new entry
                    startup = {
                        "name": row["name"],
                        "description": row.get("tagline", ""),
                        "source": "Product Hunt",
                        "github_url": "",
                        "website": row.get("website", ""),
                        "github_stars": 0,
                        "github_forks": 0,
                        "star_velocity": 0,
                        "momentum_score": 0,
                        "language": "",
                        "topics": row.get("topics", ""),
                        "founded_year": pd.to_datetime(row.get("launch_date", "")).year if pd.notnull(row.get("launch_date")) else None,
                        "funding_total": 0,
                        "location": "",
                        "ph_upvotes": row.get("upvotes", 0),
                        "ph_comments": row.get("comments", 0),
                        "launch_date": row.get("launch_date", ""),
                    }
                    all_startups.append(startup)

        df = pd.DataFrame(all_startups)

        # Calculate combined momentum score
        if not df.empty:
            df["combined_momentum"] = (
                df.get("momentum_score", 0) +
                (df.get("ph_upvotes", 0).fillna(0) * 0.5) +
                (df.get("ph_comments", 0).fillna(0) * 1.0)
            )
            df = df.sort_values("combined_momentum", ascending=False).reset_index(drop=True)

        print(f"✓ Merged {len(df)} unique startups")
        print(f"  - GitHub sources: {len([s for s in all_startups if 'GitHub' in s.get('source', '')])}")
        print(f"  - Product Hunt sources: {len([s for s in all_startups if s.get('source') == 'Product Hunt'])}")

        return df

    def load_manual_enrichment(self, csv_path: str = "data/manual_enrichment.csv") -> pd.DataFrame:
        """
        Load manually enriched data (funding, founder info from Crunchbase lookups).

        CSV should have columns:
        - name: Startup name (must match)
        - funding_total: Total funding in USD
        - last_funding_round: Series A, B, etc.
        - investors: Comma-separated investor names
        - founder: Founder name(s)

        Args:
            csv_path: Path to manual enrichment CSV

        Returns:
            DataFrame with enrichment data
        """
        if os.path.exists(csv_path):
            print(f"\nLoading manual enrichment from {csv_path}")
            try:
                df = pd.read_csv(csv_path)
                print(f"✓ Loaded enrichment for {len(df)} startups")
                return df
            except Exception as e:
                print(f"✗ Error loading enrichment: {e}")

        return pd.DataFrame()

    def apply_manual_enrichment(self, df: pd.DataFrame, enrichment_df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply manual enrichment data to the main dataset.

        Args:
            df: Main startup dataset
            enrichment_df: Manual enrichment data

        Returns:
            Enriched DataFrame
        """
        if enrichment_df.empty:
            return df

        print("\nApplying manual enrichment...")

        for _, enrich_row in enrichment_df.iterrows():
            name = enrich_row["name"]

            # Find matching startup
            mask = df["name"].str.lower() == name.lower()

            if mask.any():
                # Update with enrichment data
                for col in enrichment_df.columns:
                    if col != "name" and col in df.columns:
                        df.loc[mask, col] = enrich_row[col]

                print(f"  ✓ Enriched {name}")

        return df

    def get_combined_data(self,
                         use_cache: bool = True,
                         cache_max_age_hours: int = 24,
                         apply_enrichment: bool = True) -> pd.DataFrame:
        """
        Get complete combined dataset from all sources.

        Args:
            use_cache: Whether to use cached data
            cache_max_age_hours: Maximum cache age in hours
            apply_enrichment: Whether to apply manual enrichment

        Returns:
            Complete startup dataset
        """
        # Fetch from all sources
        sources = self.fetch_all_sources(
            use_github=True,
            use_producthunt=True,
            use_cache=use_cache,
            cache_max_age_hours=cache_max_age_hours
        )

        # Merge datasets
        df = self.merge_datasets(
            sources.get("github", pd.DataFrame()),
            sources.get("producthunt", pd.DataFrame())
        )

        # Apply manual enrichment if available
        if apply_enrichment:
            enrichment_df = self.load_manual_enrichment()
            if not enrichment_df.empty:
                df = self.apply_manual_enrichment(df, enrichment_df)

        # Save combined dataset
        self.save_combined_data(df)

        return df

    def save_combined_data(self, df: pd.DataFrame):
        """Save combined dataset to cache."""
        cache_path = os.path.join(self.cache_dir, "combined_startups.csv")
        df.to_csv(cache_path, index=False)

        metadata = {
            "last_updated": datetime.now().isoformat(),
            "record_count": len(df),
            "sources": ["GitHub", "Product Hunt", "Manual Enrichment"]
        }
        metadata_path = os.path.join(self.cache_dir, "combined_startups.csv.meta.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"\n✓ Saved combined dataset to {cache_path}")


if __name__ == "__main__":
    # Test the hybrid fetcher
    import os

    github_token = os.getenv("GITHUB_TOKEN")
    fetcher = HybridStartupFetcher(github_token=github_token)

    # Fetch and combine all data
    df = fetcher.get_combined_data(use_cache=True, cache_max_age_hours=24)

    # Display results
    if not df.empty:
        print("\n" + "="*80)
        print("COMBINED STARTUP DATASET")
        print("="*80)
        print(f"Total startups: {len(df)}")
        print("\nTop 10 by momentum:")
        print(df[["name", "source", "github_stars", "star_velocity", "combined_momentum"]].head(10).to_string())
    else:
        print("No data available.")
