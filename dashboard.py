"""Interactive dashboard for visualizing startup trends."""

import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Optional
import config
from utils import format_funding


class StartupDashboard:
    """Creates an interactive dashboard for startup trends visualization."""

    def __init__(self, data: pd.DataFrame):
        """Initialize dashboard with startup data."""
        self.data = data
        self.app = dash.Dash(__name__, suppress_callback_exceptions=True)
        self.setup_layout()
        self.setup_callbacks()

    def setup_layout(self):
        """Set up the dashboard layout."""
        self.app.layout = html.Div([
            html.Div([
                html.H1("Startup Trends Dashboard",
                       style={"textAlign": "center", "color": "#2c3e50", "marginBottom": "10px"}),
                html.P("Powered by Claude AI for Natural Language Categorization",
                      style={"textAlign": "center", "color": "#7f8c8d", "marginBottom": "30px"})
            ]),

            # Summary Statistics
            html.Div([
                html.Div([
                    html.Div([
                        html.H3(f"{len(self.data)}", style={"margin": "0", "color": "#3498db"}),
                        html.P("Total Startups", style={"margin": "5px 0 0 0", "color": "#7f8c8d"})
                    ], className="stat-box", style={
                        "backgroundColor": "#ecf0f1",
                        "padding": "20px",
                        "borderRadius": "10px",
                        "textAlign": "center"
                    }),
                ], style={"width": "30%", "display": "inline-block", "padding": "10px"}),

                html.Div([
                    html.Div([
                        html.H3(f"{self.data['category'].nunique()}", style={"margin": "0", "color": "#e74c3c"}),
                        html.P("Categories", style={"margin": "5px 0 0 0", "color": "#7f8c8d"})
                    ], className="stat-box", style={
                        "backgroundColor": "#ecf0f1",
                        "padding": "20px",
                        "borderRadius": "10px",
                        "textAlign": "center"
                    }),
                ], style={"width": "30%", "display": "inline-block", "padding": "10px"}),

                html.Div([
                    html.Div([
                        html.H3(format_funding(self.data['funding_total'].sum()),
                               style={"margin": "0", "color": "#27ae60"}),
                        html.P("Total Funding", style={"margin": "5px 0 0 0", "color": "#7f8c8d"})
                    ], className="stat-box", style={
                        "backgroundColor": "#ecf0f1",
                        "padding": "20px",
                        "borderRadius": "10px",
                        "textAlign": "center"
                    }),
                ], style={"width": "30%", "display": "inline-block", "padding": "10px"}),
            ], style={"marginBottom": "30px"}),

            # Filters
            html.Div([
                html.Label("Filter by Category:", style={"fontWeight": "bold", "marginBottom": "10px"}),
                dcc.Dropdown(
                    id="category-filter",
                    options=[{"label": "All Categories", "value": "all"}] +
                            [{"label": cat, "value": cat} for cat in sorted(self.data["category"].unique())],
                    value="all",
                    style={"marginBottom": "20px"}
                ),
            ], style={"marginBottom": "30px"}),

            # Visualizations
            html.Div([
                html.Div([
                    html.H3("Startups by Category", style={"textAlign": "center"}),
                    dcc.Graph(id="category-pie-chart")
                ], style={"width": "48%", "display": "inline-block", "padding": "10px"}),

                html.Div([
                    html.H3("Funding by Category", style={"textAlign": "center"}),
                    dcc.Graph(id="funding-bar-chart")
                ], style={"width": "48%", "display": "inline-block", "padding": "10px"}),
            ], style={"marginBottom": "30px"}),

            html.Div([
                html.Div([
                    html.H3("Top Themes", style={"textAlign": "center"}),
                    dcc.Graph(id="themes-chart")
                ], style={"width": "48%", "display": "inline-block", "padding": "10px"}),

                html.Div([
                    html.H3("Funding Distribution", style={"textAlign": "center"}),
                    dcc.Graph(id="funding-scatter")
                ], style={"width": "48%", "display": "inline-block", "padding": "10px"}),
            ], style={"marginBottom": "30px"}),

            # Data Table
            html.Div([
                html.H3("Startup Details", style={"textAlign": "center"}),
                html.Div(id="startup-table")
            ], style={"marginTop": "30px"})
        ], style={"padding": "20px", "fontFamily": "Arial, sans-serif"})

    def setup_callbacks(self):
        """Set up interactive callbacks."""

        @self.app.callback(
            [Output("category-pie-chart", "figure"),
             Output("funding-bar-chart", "figure"),
             Output("themes-chart", "figure"),
             Output("funding-scatter", "figure"),
             Output("startup-table", "children")],
            [Input("category-filter", "value")]
        )
        def update_dashboard(selected_category):
            # Filter data
            if selected_category == "all":
                filtered_data = self.data
            else:
                filtered_data = self.data[self.data["category"] == selected_category]

            # Category Pie Chart
            category_counts = filtered_data["category"].value_counts().reset_index()
            category_counts.columns = ["category", "count"]

            pie_fig = px.pie(
                category_counts,
                values="count",
                names="category",
                title="Distribution by Category",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            pie_fig.update_traces(textposition="inside", textinfo="percent+label")

            # Funding Bar Chart
            funding_by_category = filtered_data.groupby("category")["funding_total"].sum().reset_index()
            # Use smart formatting: show in millions if < $1B, otherwise billions
            total_funding = funding_by_category["funding_total"].sum()
            if total_funding >= 1_000_000_000:
                funding_by_category["funding_display"] = funding_by_category["funding_total"] / 1e9
                funding_label = "Funding ($B)"
                title_text = "Total Funding by Category"
            else:
                funding_by_category["funding_display"] = funding_by_category["funding_total"] / 1e6
                funding_label = "Funding ($M)"
                title_text = "Total Funding by Category"

            funding_by_category = funding_by_category.sort_values("funding_display", ascending=True)

            bar_fig = px.bar(
                funding_by_category,
                x="funding_display",
                y="category",
                orientation="h",
                title=title_text,
                labels={"funding_display": funding_label, "category": "Category"},
                color="funding_display",
                color_continuous_scale="Viridis"
            )

            # Themes Chart
            all_themes = []
            for themes_str in filtered_data["themes"].dropna():
                if themes_str:
                    themes = [t.strip() for t in str(themes_str).split(",")]
                    all_themes.extend(themes)

            from collections import Counter
            theme_counts = Counter(all_themes)
            top_themes = theme_counts.most_common(10)

            themes_df = pd.DataFrame(top_themes, columns=["theme", "count"])
            themes_fig = px.bar(
                themes_df,
                x="count",
                y="theme",
                orientation="h",
                title="Most Common Themes",
                labels={"count": "Count", "theme": "Theme"},
                color="count",
                color_continuous_scale="Blues"
            )

            # Funding Scatter Plot
            scatter_data = filtered_data.copy()
            scatter_data["funding_millions"] = scatter_data["funding_total"] / 1e6

            scatter_fig = px.scatter(
                scatter_data,
                x="founded_year",
                y="funding_millions",
                size="funding_millions",
                color="category",
                hover_data=["name", "description"],
                title="Funding vs Founded Year",
                labels={"founded_year": "Founded Year", "funding_millions": "Funding ($M)"},
                color_discrete_sequence=px.colors.qualitative.Plotly
            )

            # Data Table
            # Select columns including source, github_stars
            table_columns = ["name", "source", "category", "github_stars", "funding_total", "founded_year"]

            # Only include columns that exist in the dataframe
            available_columns = [col for col in table_columns if col in filtered_data.columns]
            table_data = filtered_data[available_columns].copy()

            # Format funding
            if "funding_total" in table_data.columns:
                table_data["funding_total"] = table_data["funding_total"].fillna(0).apply(format_funding)

            # Format github_stars
            if "github_stars" in table_data.columns:
                table_data["github_stars"] = table_data["github_stars"].fillna(0).apply(lambda x: f"{int(x):,}" if x > 0 else "N/A")

            # Rename columns for display
            display_names = {
                "name": "Name",
                "source": "Source",
                "category": "Category",
                "github_stars": "GitHub ⭐",
                "funding_total": "Funding",
                "founded_year": "Founded"
            }

            # Create table with hyperlinks for name column
            table_rows = []
            for i in range(len(table_data)):
                row_cells = []
                for col in table_data.columns:
                    if col == "name":
                        # Create hyperlink for name
                        name = table_data.iloc[i]["name"]
                        # Get URL from github_url or website
                        url = ""
                        if "github_url" in filtered_data.columns:
                            url = filtered_data.iloc[i].get("github_url", "")
                        if not url and "website" in filtered_data.columns:
                            url = filtered_data.iloc[i].get("website", "")

                        if url:
                            cell = html.Td(
                                html.A(name, href=url, target="_blank",
                                      style={"color": "#3498db", "textDecoration": "none"}),
                                style={"padding": "10px", "borderBottom": "1px solid #ddd"}
                            )
                        else:
                            cell = html.Td(name, style={"padding": "10px", "borderBottom": "1px solid #ddd"})
                    else:
                        cell = html.Td(
                            table_data.iloc[i][col],
                            style={"padding": "10px", "borderBottom": "1px solid #ddd"}
                        )
                    row_cells.append(cell)
                table_rows.append(html.Tr(row_cells))

            table = html.Table([
                html.Thead(
                    html.Tr([
                        html.Th(display_names.get(col, col),
                               style={"padding": "10px", "backgroundColor": "#3498db", "color": "white"})
                        for col in table_data.columns
                    ])
                ),
                html.Tbody(table_rows)
            ], style={"width": "100%", "borderCollapse": "collapse", "marginTop": "20px"})

            return pie_fig, bar_fig, themes_fig, scatter_fig, table

    def run(self, host: str = None, port: int = None, debug: bool = True):
        """Run the dashboard server."""
        host = host or config.DASHBOARD_HOST
        port = port or config.DASHBOARD_PORT

        print(f"\n{'='*60}")
        print(f"Starting Startup Trends Dashboard...")
        print(f"Dashboard URL: http://{host}:{port}")
        print(f"{'='*60}\n")

        self.app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    # Load categorized data
    import os

    data_path = "data/categorized_startups.csv"

    if not os.path.exists(data_path):
        print("Categorized data not found. Running categorization first...")
        from data_fetcher import StartupDataFetcher
        from categorizer import StartupCategorizer

        fetcher = StartupDataFetcher()
        df = fetcher.load_data()

        categorizer = StartupCategorizer()
        df = categorizer.categorize_startups(df)

        df.to_csv(data_path, index=False)
        print(f"Saved categorized data to {data_path}")
    else:
        print(f"Loading categorized data from {data_path}")
        df = pd.read_csv(data_path)

    # Create and run dashboard
    dashboard = StartupDashboard(df)
    dashboard.run()
