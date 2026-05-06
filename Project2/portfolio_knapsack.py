"""
Stock-selection helpers for the MSML606 Project 2 notebook.

The project models each stock as one 0/1 knapsack item:

* value: recent momentum score
* weight: recent volatility converted to integer risk points
* capacity: a fixed total risk budget
"""

from __future__ import annotations

from bisect import bisect_right
from collections import defaultdict
from dataclasses import dataclass
import csv
import math
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple, Union


# Stores the price history for one stock ticker
@dataclass(frozen=True)
class PriceHistory:
    # dates: all available trading dates for one stock.
    # prices: adjusted closing prices for those same dates.
    # The dates and prices match by position, and are sorted chronologically.

    dates: List[str]
    prices: List[float]


# Represents one stock after it has been converted into a knapsack item
@dataclass(frozen=True)
class StockCandidate:
    """
    ticker: stock ticker, like AAPL or MSFT.
    decision_date: date when the algorithm makes the selection.
    price: stock price on the decision date.
    return_5d: return over the last 5 trading days.
    return_20d: return over the last 20 trading days.
    momentum_value: the “value” used in knapsack.
    volatility_20d: recent volatility, used as risk.
    risk_points: volatility converted into integer weight.
    future_return_20d: next 20-day return, used only for later evaluation.
    """

    ticker: str
    decision_date: str
    price: float
    return_5d: float
    return_20d: float
    momentum_value: float
    volatility_20d: float
    risk_points: int
    future_return_20d: Optional[float]

    # This tells us how much momentum the stock gives per risk point
    # The value-to-risk ratio is used for greedy ranking and display
    @property
    def value_to_risk(self) -> float:
        return (self.momentum_value / self.risk_points)


# Stores the output of either the DP algorithm or the greedy algorithm
@dataclass(frozen=True)
class PortfolioResult:
    """
    selected: list of selected StockCandidate objects.
    total_value: total momentum score of the selected stocks.
    total_risk_points: total risk used by the selected stocks.
    capacity_points: maximum allowed risk budget.
    """

    selected: List[StockCandidate]
    total_value: float
    total_risk_points: int
    capacity_points: int

    # This calculates the average next-20-day return of the selected stocks
    # It is used for later evaluation, and is not part of the knapsack optimization.
    @property
    def average_future_return(self) -> Optional[float]:
        returns = [
            stock.future_return_20d
            for stock in self.selected
            if stock.future_return_20d is not None
        ]
        if not returns:
            return None
        return (sum(returns) / len(returns))

# Reads the Kaggle CSV file and prepares the clean input data as a dictionary:
# mapping ticker -> PriceHistory, 
# where PriceHistory contains all the dates and prices for that stock.
def load_stock_history(
        csv_path: Union[str, Path],
        price_column: str = "Adj Close",
    ) -> Dict[str, PriceHistory]:

    # Check whether the CSV file exists
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Could not find {csv_path}. Place SP500_Historical_Data.csv in the project folder."
        )

    # Use a defaultdict to accumulate dates and prices for each ticker
    raw: Dict[str, Tuple[List[str], List[float]]] = defaultdict(lambda: ([], []))

    # Read the CSV file and populate the raw dictionary
    # Checks required columns: Ticker, Date, Adj Close, and Close
    with csv_path.open(newline="") as file:
        reader = csv.DictReader(file)
        required_columns = {"Ticker", "Date", price_column, "Close"}
        missing = required_columns.difference(reader.fieldnames or [])
        if missing:
            missing_text = ", ".join(sorted(missing))
            raise ValueError(f"CSV file is missing required column(s): {missing_text}")

        # Process each row, extracting ticker, date, and price
        for row in reader:
            ticker = row["Ticker"].strip()
            if not ticker:
                continue
            
            price_text = row.get(price_column) or row.get("Close") or ""
            try:
                price = float(price_text)
            except ValueError:
                continue
            
            if price <= 0:
                continue
            
            dates, prices = raw[ticker]
            dates.append(row["Date"])
            prices.append(price)

    # Convert the raw dictionary into the final dictionary
    history: Dict[str, PriceHistory] = {}
    for ticker, (dates, prices) in raw.items():
        if any(dates[i] > dates[i + 1] for i in range(len(dates) - 1)):
            ordered = sorted(zip(dates, prices), key=lambda item: item[0])
            dates = [date for date, _ in ordered]
            prices = [price for _, price in ordered]
        history[ticker] = PriceHistory(dates=dates, prices=prices)

    return history

# Collects every date that appears in the dataset and returns them sorted
def all_market_dates(history: Dict[str, PriceHistory]) -> List[str]:
    return sorted({date for stock in history.values() for date in stock.dates})

# Chooses a recent decision date while still leaving enough future data for evaluation
def choose_decision_date(
        history: Dict[str, PriceHistory],
        future_days: int = 20,
    ) -> str:

    # Validate future_days and ensure there are enough dates for the decision date
    dates = all_market_dates(history)
    if not dates:
        raise ValueError("No dates were found in the price history.")
    if future_days < 0:
        raise ValueError("future_days must be non-negative.")
    if future_days >= len(dates):
        raise ValueError("future_days is larger than the available date history.")
    return dates[-future_days - 1]
