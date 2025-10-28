# Startup Trends Dashboard

An interactive dashboard that uses Claude AI to automatically categorize startups by theme and visualize funding trends across different sectors.

## Features

- **Automated Categorization**: Uses Claude's natural language understanding to categorize startups into themes like "AI Infrastructure," "Digital Health," "Developer Tools," and more
- **Natural Language Clustering**: Claude analyzes startup descriptions to identify patterns and group similar companies
- **Interactive Visualizations**: Explore funding trends, category distributions, and popular themes
- **Real-time Analysis**: Get instant insights into the startup ecosystem

## Project Structure

```
startup-trends-dashboard/
├── main.py                    # Main entry point
├── config.py                  # Configuration settings
├── data_fetcher.py           # Data fetching module
├── categorizer.py            # Claude AI categorization
├── dashboard.py              # Interactive dashboard
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── data/                     # Data directory (auto-created)
│   ├── sample_startups.csv
│   └── categorized_startups.csv
└── README.md                 # This file
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- An Anthropic API key (get one at https://console.anthropic.com)

### Installation

1. **Navigate to the project directory**:
   ```bash
   cd ~/Claude/startup-trends-dashboard
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your API key**:
   ```bash
   cp .env.example .env
   ```

   Then edit `.env` and add your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

## Usage

### Quick Start

Run the application with default settings:

```bash
python main.py
```

This will:
1. Load sample startup data
2. Use Claude AI to categorize startups by theme
3. Launch an interactive dashboard at http://127.0.0.1:8050

### Command Line Options

```bash
# Force recategorization (useful after updating data)
python main.py --recategorize

# Run on a different port
python main.py --port 8080

# Only categorize data without launching dashboard
python main.py --no-dashboard
```

### Using Individual Modules

**Fetch Data**:
```python
from data_fetcher import StartupDataFetcher

fetcher = StartupDataFetcher()
df = fetcher.load_data()
print(df.head())
```

**Categorize with Claude**:
```python
from categorizer import StartupCategorizer

categorizer = StartupCategorizer()
categorized_df = categorizer.categorize_startups(df)
summary = categorizer.get_category_summary(categorized_df)
```

**Launch Dashboard**:
```python
from dashboard import StartupDashboard

dashboard = StartupDashboard(categorized_df)
dashboard.run()
```

## How It Works

### 1. Data Collection

The application includes sample data from well-known startups. In production, you could extend this to:
- Fetch from Crunchbase API
- Scrape Y Combinator's company directory
- Import your own CSV/JSON data

### 2. Claude AI Categorization

The categorizer sends startup descriptions to Claude with a carefully crafted prompt that asks it to:
- Identify the primary category (e.g., "AI Infrastructure", "Fintech")
- Assign subcategories for more granular classification
- Extract relevant themes and tags

Claude analyzes each startup's description using natural language understanding to create meaningful, consistent categories.

### 3. Interactive Dashboard

The Dash-based dashboard provides:
- **Category Distribution**: Pie chart showing startup distribution across categories
- **Funding Analysis**: Bar charts of total funding by category
- **Theme Trends**: Visualization of most common themes
- **Scatter Plots**: Funding vs. founding year analysis
- **Data Table**: Detailed view of all startups with filtering

## Dashboard Features

### Key Metrics
- Total number of startups analyzed
- Number of unique categories identified
- Total funding across all startups

### Interactive Filters
- Filter by category to focus on specific sectors
- Dynamic updates across all visualizations

### Visualizations
1. **Category Distribution**: See which sectors have the most startups
2. **Funding by Category**: Identify which categories attract the most capital
3. **Theme Analysis**: Discover trending technologies and focus areas
4. **Timeline View**: Understand how funding patterns have evolved

## Customization

### Adding Your Own Data

Create a CSV file with the following columns:
- `name`: Startup name
- `description`: Company description
- `funding_total`: Total funding in USD
- `founded_year`: Year founded
- `location`: Company location

Update `data_fetcher.py` to load your custom data.

### Modifying Categories

Edit the prompt in `categorizer.py` to customize how Claude categorizes startups. You can:
- Add specific categories you're interested in
- Request additional metadata
- Change the granularity of classification

### Dashboard Styling

Modify `dashboard.py` to customize:
- Colors and themes
- Chart types
- Layout and organization
- Additional metrics

## Example Output

```
======================================================================
  STARTUP TRENDS DASHBOARD
  Powered by Claude AI
======================================================================

Step 1: Loading startup data...
----------------------------------------------------------------------
✓ Loaded 20 startups

Step 2: Categorizing startups with Claude AI...
----------------------------------------------------------------------
This may take a moment as Claude analyzes each startup...

✓ Categorization complete!
✓ Results saved to data/categorized_startups.csv

Category Summary:
----------------------------------------------------------------------
  AI Infrastructure: 5 startups
  Developer Tools: 4 startups
  Fintech: 3 startups
  Digital Health: 3 startups
  Enterprise Software: 3 startups
  B2C Marketplace: 2 startups

Step 3: Launching interactive dashboard...
----------------------------------------------------------------------
Dashboard URL: http://127.0.0.1:8050
```

## Technologies Used

- **Claude AI (Anthropic)**: Natural language categorization
- **Dash/Plotly**: Interactive data visualization
- **Pandas**: Data manipulation and analysis
- **Python 3**: Core programming language

## Troubleshooting

### "ANTHROPIC_API_KEY not found"
Make sure you've created a `.env` file and added your API key.

### Dashboard won't start
Check if port 8050 is already in use. Try a different port with `--port 8051`.

### Categorization errors
Verify your API key is valid and you have available credits in your Anthropic account.

## Future Enhancements

Potential additions to the project:
- Integration with live Crunchbase/YC APIs
- Time-series analysis of funding trends
- Comparison across different regions
- Export reports to PDF/Excel
- Machine learning predictions based on historical data

## License

This project is open source and available for educational purposes.

## Contributing

Feel free to submit issues and enhancement requests!
