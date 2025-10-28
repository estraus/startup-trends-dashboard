"""Utility functions for the Startup Trends Dashboard."""

def format_funding(amount: float) -> str:
    """
    Format funding amount intelligently.
    - If < $1B, return in millions (e.g., "$125.5M")
    - If >= $1B, return in billions (e.g., "$2.3B")

    Args:
        amount: Funding amount in USD

    Returns:
        Formatted string with appropriate unit
    """
    if amount >= 1_000_000_000:
        # Format in billions
        billions = amount / 1_000_000_000
        return f"${billions:.1f}B"
    else:
        # Format in millions
        millions = amount / 1_000_000
        return f"${millions:.1f}M"


def format_funding_for_display(amount: float, decimals: int = 1) -> str:
    """
    Format funding for display with more control over decimals.

    Args:
        amount: Funding amount in USD
        decimals: Number of decimal places

    Returns:
        Formatted string
    """
    if amount >= 1_000_000_000:
        value = amount / 1_000_000_000
        return f"${value:.{decimals}f}B"
    else:
        value = amount / 1_000_000
        return f"${value:.{decimals}f}M"


if __name__ == "__main__":
    # Test the formatting function
    test_values = [
        50_000_000,      # 50M
        500_000_000,     # 500M
        999_000_000,     # 999M
        1_000_000_000,   # 1B
        1_500_000_000,   # 1.5B
        11_300_000_000,  # 11.3B
    ]

    print("Testing funding formatting:")
    for value in test_values:
        print(f"  {value:>15,} -> {format_funding(value)}")
