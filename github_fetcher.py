"""Fetch startup data from GitHub using their public API."""

import requests
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import time
import json
import os


class GitHubStartupFetcher:
    """Fetch trending startups and momentum metrics from GitHub."""

    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize GitHub fetcher.

        Args:
            github_token: Optional GitHub personal access token for higher rate limits
        """
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if github_token:
            self.headers["Authorization"] = f"token {github_token}"

        self.cache_dir = "data/cache"
        os.makedirs(self.cache_dir, exist_ok=True)

    def get_trending_startups(self,
                             topics: List[str] = ["startup", "saas", "ai", "fintech"],
                             min_stars: int = 100,
                             days_back: int = 90,
                             limit: int = 50) -> pd.DataFrame:
        """
        Fetch trending startup repositories from GitHub.

        Args:
            topics: Topics to search for
            min_stars: Minimum number of stars
            days_back: Look back this many days
            limit: Maximum number of results

        Returns:
            DataFrame with startup repository data
        """
        print(f"Fetching trending startups from GitHub...")
        print(f"Topics: {', '.join(topics)}")
        print(f"Minimum stars: {min_stars}")

        all_repos = []

        # Calculate date threshold
        date_threshold = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

        for topic in topics:
            try:
                # Search for repositories
                query = f"topic:{topic} stars:>{min_stars} created:>{date_threshold}"
                url = f"{self.base_url}/search/repositories"
                params = {
                    "q": query,
                    "sort": "stars",
                    "order": "desc",
                    "per_page": min(100, limit)
                }

                response = requests.get(url, headers=self.headers, params=params, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    repos = data.get("items", [])
                    all_repos.extend(repos)
                    print(f"  ✓ Found {len(repos)} repos for '{topic}'")

                    # Respect rate limits
                    time.sleep(1)
                elif response.status_code == 403:
                    print(f"  ✗ Rate limit exceeded. Add GITHUB_TOKEN to .env for higher limits.")
                    break
                else:
                    print(f"  ✗ Error fetching '{topic}': {response.status_code}")

            except Exception as e:
                print(f"  ✗ Error with topic '{topic}': {e}")

        if not all_repos:
            print("No repositories found.")
            return pd.DataFrame()

        # Remove duplicates
        seen_ids = set()
        unique_repos = []
        for repo in all_repos:
            if repo["id"] not in seen_ids:
                seen_ids.add(repo["id"])
                unique_repos.append(repo)

        # Convert to DataFrame
        startups = []
        for repo in unique_repos[:limit]:
            startup = {
                "name": repo.get("owner", {}).get("login", "Unknown"),
                "repo_name": repo.get("name", ""),
                "description": repo.get("description", "No description available"),
                "github_url": repo.get("html_url", ""),
                "homepage": repo.get("homepage", ""),
                "stars": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "watchers": repo.get("watchers_count", 0),
                "open_issues": repo.get("open_issues_count", 0),
                "language": repo.get("language", "Unknown"),
                "topics": ", ".join(repo.get("topics", [])),
                "created_at": repo.get("created_at", ""),
                "updated_at": repo.get("updated_at", ""),
                "last_push": repo.get("pushed_at", ""),
            }
            startups.append(startup)

        df = pd.DataFrame(startups)

        # Calculate momentum score (simple weighted metric)
        if not df.empty:
            df["momentum_score"] = (
                df["stars"] * 1.0 +
                df["forks"] * 2.0 +
                df["watchers"] * 0.5
            )
            df = df.sort_values("momentum_score", ascending=False).reset_index(drop=True)

        print(f"\n✓ Found {len(df)} unique startup repositories")

        return df

    def enrich_with_org_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Enrich startup data with GitHub organization information.

        Args:
            df: DataFrame with startup data

        Returns:
            Enriched DataFrame
        """
        print("\nEnriching with organization data...")

        enriched_data = []

        for idx, row in df.iterrows():
            org_name = row["name"]

            try:
                # Fetch organization data
                url = f"{self.base_url}/users/{org_name}"
                response = requests.get(url, headers=self.headers, timeout=10)

                if response.status_code == 200:
                    org_data = response.json()

                    row["org_type"] = org_data.get("type", "User")
                    row["company"] = org_data.get("company", "")
                    row["location"] = org_data.get("location", "")
                    row["email"] = org_data.get("email", "")
                    row["bio"] = org_data.get("bio", "")
                    row["public_repos"] = org_data.get("public_repos", 0)
                    row["followers"] = org_data.get("followers", 0)

                    print(f"  ✓ Enriched {org_name}")
                else:
                    print(f"  ✗ Could not fetch org data for {org_name}")

                enriched_data.append(row)

                # Respect rate limits
                time.sleep(0.5)

            except Exception as e:
                print(f"  ✗ Error enriching {org_name}: {e}")
                enriched_data.append(row)

        return pd.DataFrame(enriched_data)

    def calculate_growth_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate growth metrics like star velocity.

        Args:
            df: DataFrame with startup data

        Returns:
            DataFrame with growth metrics
        """
        if df.empty:
            return df

        # Calculate days since creation
        df["created_at"] = pd.to_datetime(df["created_at"], utc=True)
        df["days_old"] = (pd.Timestamp.now(tz='UTC') - df["created_at"]).dt.days

        # Calculate star velocity (stars per day)
        df["star_velocity"] = df["stars"] / df["days_old"].replace(0, 1)

        # Calculate fork ratio
        df["fork_ratio"] = df["forks"] / df["stars"].replace(0, 1)

        return df

    def save_to_cache(self, df: pd.DataFrame, filename: str = "github_startups.csv"):
        """Save data to cache."""
        cache_path = os.path.join(self.cache_dir, filename)
        df.to_csv(cache_path, index=False)

        # Save metadata
        metadata = {
            "last_updated": datetime.now().isoformat(),
            "record_count": len(df),
            "source": "GitHub API"
        }
        metadata_path = os.path.join(self.cache_dir, f"{filename}.meta.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"\n✓ Cached data to {cache_path}")

    def load_from_cache(self, filename: str = "github_startups.csv",
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
                print(f"Loading cached data (age: {age_hours:.1f} hours)")
                return pd.read_csv(cache_path)
            else:
                print(f"Cache expired (age: {age_hours:.1f} hours > {max_age_hours} hours)")

        return None


if __name__ == "__main__":
    # Test the GitHub fetcher
    fetcher = GitHubStartupFetcher()

    # Try to load from cache first
    df = fetcher.load_from_cache(max_age_hours=24)

    if df is None:
        # Fetch fresh data
        df = fetcher.get_trending_startups(
            topics=["startup", "saas", "ai-startup", "fintech"],
            min_stars=50,
            days_back=180,
            limit=30
        )

        if not df.empty:
            # Calculate growth metrics
            df = fetcher.calculate_growth_metrics(df)

            # Save to cache
            fetcher.save_to_cache(df)

    # Display results
    if not df.empty:
        print("\n" + "="*80)
        print("TOP TRENDING STARTUP REPOSITORIES")
        print("="*80)
        print(df[["name", "repo_name", "stars", "forks", "star_velocity", "momentum_score"]].head(10).to_string())
    else:
        print("No data available.")
