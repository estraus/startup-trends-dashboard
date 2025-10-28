#!/usr/bin/env python3
"""
Startup Trends Dashboard - Main Entry Point

This application fetches startup data, uses Claude AI to categorize them by theme,
and displays an interactive dashboard with trends and insights.
"""

import sys
import argparse
from data_fetcher import StartupDataFetcher
from categorizer import StartupCategorizer
from dashboard import StartupDashboard
import pandas as pd
import os


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(
        description="Startup Trends Dashboard - Analyze and visualize startup trends using Claude AI"
    )
    parser.add_argument(
        "--recategorize",
        action="store_true",
        help="Force recategorization of startups even if cached data exists"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8050,
        help="Port to run the dashboard server (default: 8050)"
    )
    parser.add_argument(
        "--no-dashboard",
        action="store_true",
        help="Only categorize data without launching dashboard"
    )

    args = parser.parse_args()

    print("\n" + "="*70)
    print("  STARTUP TRENDS DASHBOARD")
    print("  Powered by Claude AI")
    print("="*70 + "\n")

    # Check for API key
    import config
    if not config.ANTHROPIC_API_KEY:
        print("ERROR: ANTHROPIC_API_KEY not found!")
        print("\nPlease follow these steps:")
        print("1. Copy .env.example to .env")
        print("2. Add your Anthropic API key to the .env file")
        print("3. Run the application again\n")
        sys.exit(1)

    # Step 1: Fetch or load data
    print("Step 1: Loading startup data...")
    print("-" * 70)
    fetcher = StartupDataFetcher()

    # Load data based on configuration
    if config.DATA_SOURCE == "url" and config.DATA_SOURCE_URL:
        print(f"Data source: Remote URL")
        print(f"URL: {config.DATA_SOURCE_URL}")
        df = fetcher.load_data(source="url", url=config.DATA_SOURCE_URL)
    else:
        print(f"Data source: {config.DATA_SOURCE}")
        df = fetcher.load_data(source=config.DATA_SOURCE)

    print(f"✓ Loaded {len(df)} startups\n")

    # Step 2: Categorize with Claude
    categorized_data_path = "data/categorized_startups.csv"

    if args.recategorize or not os.path.exists(categorized_data_path):
        print("Step 2: Categorizing startups with Claude AI...")
        print("-" * 70)
        print("This may take a moment as Claude analyzes each startup...\n")

        try:
            categorizer = StartupCategorizer()
            df = categorizer.categorize_startups(df)

            # Save categorized data
            df.to_csv(categorized_data_path, index=False)
            print(f"✓ Categorization complete!")
            print(f"✓ Results saved to {categorized_data_path}\n")

            # Show summary
            summary = categorizer.get_category_summary(df)
            print("Category Summary:")
            print("-" * 70)
            for category, count in summary["categories"].items():
                print(f"  {category}: {count} startups")
            print()

        except Exception as e:
            print(f"✗ Error during categorization: {e}")
            print("\nPlease check your API key and try again.")
            sys.exit(1)
    else:
        print("Step 2: Loading cached categorization data...")
        print("-" * 70)
        df = pd.read_csv(categorized_data_path)
        print(f"✓ Loaded categorized data from cache")
        print(f"  (Use --recategorize to force new categorization)\n")

    # Stop here if --no-dashboard is specified
    if args.no_dashboard:
        print("✓ Data processing complete!")
        print(f"Categorized data saved to: {categorized_data_path}\n")
        return

    # Step 3: Launch dashboard
    print("Step 3: Launching interactive dashboard...")
    print("-" * 70)

    try:
        dashboard = StartupDashboard(df)
        dashboard.run(port=args.port)
    except KeyboardInterrupt:
        print("\n\n✓ Dashboard shut down gracefully.")
    except Exception as e:
        print(f"\n✗ Error launching dashboard: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
