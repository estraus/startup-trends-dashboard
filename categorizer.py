"""Module for categorizing startups using Claude API."""

import anthropic
import pandas as pd
from typing import List, Dict
import json
import config


class StartupCategorizer:
    """Uses Claude API to categorize startups by theme using natural language."""

    def __init__(self, api_key: str = None):
        """Initialize the categorizer with Claude API."""
        self.api_key = api_key or config.ANTHROPIC_API_KEY
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found. Please set it in .env file.")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = config.CLAUDE_MODEL

    def categorize_startups(self, startups_df: pd.DataFrame) -> pd.DataFrame:
        """
        Categorize startups using Claude's natural language understanding.

        Args:
            startups_df: DataFrame with startup information

        Returns:
            DataFrame with added 'category' and 'subcategory' columns
        """
        # Prepare the startup data for Claude
        startups_list = []
        for idx, row in startups_df.iterrows():
            startups_list.append({
                "id": idx,
                "name": row["name"],
                "description": row["description"]
            })

        # Create the prompt for Claude
        prompt = self._create_categorization_prompt(startups_list)

        print("Sending categorization request to Claude...")

        # Call Claude API
        message = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # Parse the response
        response_text = message.content[0].text
        print("Received categorization response from Claude")

        # Extract JSON from response
        categories = self._parse_categorization_response(response_text)

        # Add categories to dataframe
        startups_df = startups_df.copy()
        startups_df["category"] = None
        startups_df["subcategory"] = None
        startups_df["themes"] = None

        for item in categories:
            idx = item["id"]
            if idx < len(startups_df):
                startups_df.at[idx, "category"] = item.get("category", "Other")
                startups_df.at[idx, "subcategory"] = item.get("subcategory", "")
                startups_df.at[idx, "themes"] = ", ".join(item.get("themes", []))

        return startups_df

    def _create_categorization_prompt(self, startups: List[Dict]) -> str:
        """Create a prompt for Claude to categorize startups."""
        startups_json = json.dumps(startups, indent=2)

        prompt = f"""You are an expert at analyzing and categorizing startups by their business themes and focus areas.

I have a list of startups with their descriptions. Please categorize each startup into appropriate themes using natural language understanding.

For each startup, provide:
1. A primary category (e.g., "AI Infrastructure", "Digital Health", "Developer Tools", "Fintech", "Enterprise Software", etc.)
2. A subcategory (more specific classification)
3. A list of relevant themes/tags

Here are the startups:

{startups_json}

Please respond with a JSON array where each object contains:
- id: the startup's id from the input
- category: the primary category
- subcategory: a more specific subcategory
- themes: an array of relevant theme tags

Focus on creating meaningful, consistent categories that help group similar companies together. Consider aspects like:
- Technology focus (AI/ML, blockchain, cloud, etc.)
- Industry vertical (healthcare, finance, education, etc.)
- Target customer (B2B, B2C, developer tools, enterprise, etc.)
- Problem space (productivity, infrastructure, security, etc.)

Return ONLY the JSON array, no additional text."""

        return prompt

    def _parse_categorization_response(self, response: str) -> List[Dict]:
        """Parse Claude's response to extract categorization data."""
        try:
            # Try to find JSON in the response
            start_idx = response.find("[")
            end_idx = response.rfind("]") + 1

            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # If no JSON array found, try to parse the entire response
                return json.loads(response)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Response: {response}")
            return []

    def get_category_summary(self, categorized_df: pd.DataFrame) -> Dict:
        """Generate a summary of categories and their counts."""
        summary = {
            "total_startups": len(categorized_df),
            "categories": {},
            "themes": {}
        }

        # Count by category
        if "category" in categorized_df.columns:
            category_counts = categorized_df["category"].value_counts().to_dict()
            summary["categories"] = category_counts

        # Count themes
        if "themes" in categorized_df.columns:
            all_themes = []
            for themes_str in categorized_df["themes"].dropna():
                if themes_str:
                    themes = [t.strip() for t in themes_str.split(",")]
                    all_themes.extend(themes)

            from collections import Counter
            theme_counts = Counter(all_themes)
            summary["themes"] = dict(theme_counts.most_common(15))

        return summary


if __name__ == "__main__":
    from data_fetcher import StartupDataFetcher

    # Load data
    fetcher = StartupDataFetcher()
    df = fetcher.load_data()

    # Categorize
    categorizer = StartupCategorizer()
    categorized_df = categorizer.categorize_startups(df)

    # Show results
    print("\n=== Categorized Startups ===")
    print(categorized_df[["name", "category", "subcategory", "themes"]])

    # Show summary
    summary = categorizer.get_category_summary(categorized_df)
    print("\n=== Category Summary ===")
    print(json.dumps(summary, indent=2))

    # Save results
    categorized_df.to_csv("data/categorized_startups.csv", index=False)
    print("\nResults saved to data/categorized_startups.csv")
