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

# Converts raw stock prices into knapsack-ready stock candidates
def build_candidates(
        history: Dict[str, PriceHistory],
        decision_date: str,
        *,
        future_days: int = 20,
        risk_scale: int = 10_000,
        require_positive_momentum: bool = True,
        require_future_return: bool = True,
    ) -> List[StockCandidate]:

    """
    For each ticker, it:
    1. Finds the stock's latest available price on or before the decision date.
    2. Requires at least 20 previous trading days.
    3. Calculates future return if evaluation is requested.
    4. Calculates 5-day return.
    5. Calculates 20-day return.
    6. Calculates momentum value: 'momentum_value = max(0.0, 0.6 * return_5d + 0.4 * return_20d)'
    7. Calculates daily returns over the past 20 trading days.
    8. Calculates volatility from those daily returns.
    9. Converts volatility into integer risk points: 'risk_points = max(1, math.ceil(volatility * risk_scale))'
    """

    candidates: List[StockCandidate] = []

    # Check that the decision date is valid for at least some stocks
    for ticker, stock in history.items():
        index = bisect_right(stock.dates, decision_date) - 1
        # We require at least 20 previous trading days to calculate momentum and volatility
        if index < 20:
            continue
        
        # Calculate the future return if requested, and skip if it's required but not available
        if future_days > 0 and index + future_days >= len(stock.prices):
            if require_future_return:
                continue
            future_return = None
        elif future_days > 0:
            future_return = stock.prices[index + future_days] / stock.prices[index] - 1
        else:
            future_return = None

        # Calculate the momentum value based on recent returns, and skip if positive momentum is required but not met
        price_today = stock.prices[index]
        return_5d = price_today / stock.prices[index - 5] - 1
        return_20d = price_today / stock.prices[index - 20] - 1
        momentum_value = max(0.0, 0.6 * return_5d + 0.4 * return_20d)

        if require_positive_momentum and momentum_value <= 0:
            continue
        
        # Calculate the volatility based on daily returns over the past 20 trading days
        daily_returns = [
            stock.prices[day] / stock.prices[day - 1] - 1
            for day in range(index - 19, index + 1)
        ]
        average_daily_return = sum(daily_returns) / len(daily_returns)
        volatility = math.sqrt(
            sum((daily_return - average_daily_return) ** 2 for daily_return in daily_returns)
            / len(daily_returns)
        )

        # Skip stocks with non-positive volatility, as they would not make sense in the knapsack model
        if volatility <= 0:
            continue

        # Convert volatility into integer risk points, ensuring at least 1 risk point
        risk_points = max(1, math.ceil(volatility * risk_scale))
        candidates.append(
            StockCandidate(
                ticker=ticker,
                decision_date=stock.dates[index],
                price=price_today,
                return_5d=return_5d,
                return_20d=return_20d,
                momentum_value=momentum_value,
                volatility_20d=volatility,
                risk_points=risk_points,
                future_return_20d=future_return,
            )
        )

    return sorted(candidates, key=lambda stock: stock.ticker)

# Main algorithm
# Solves the 0/1 knapsack problem exactly using dynamic programming (DP)
def solve_knapsack_dp(
        candidates: Sequence[StockCandidate],
        capacity_points: int,
    ) -> PortfolioResult:

    # Validate capacity_points and ensure it's positive
    if capacity_points <= 0:
        raise ValueError("capacity_points must be positive.")

    dp = [0.0] * (capacity_points + 1)
    keep_rows: List[bytearray] = []

    for stock in candidates:
        row = bytearray(capacity_points + 1)
        weight = stock.risk_points
        value = stock.momentum_value
        
        if weight <= capacity_points:
            # Iterate backwards to ensure each stock can only be used once, as the 0/1 knapsack
            for capacity in range(capacity_points, weight - 1, -1):
                candidate_value = dp[capacity - weight] + value
                if candidate_value > dp[capacity] + 1e-15:
                    dp[capacity] = candidate_value
                    row[capacity] = 1

        keep_rows.append(row)

    best_value = max(dp)
    best_capacity = min(
        capacity
        for capacity, value in enumerate(dp)
        if abs(value - best_value) <= 1e-12
    )

    selected_indices: List[int] = []
    remaining_capacity = best_capacity
    for index in range(len(candidates) - 1, -1, -1):
        if keep_rows[index][remaining_capacity]:
            selected_indices.append(index)
            remaining_capacity -= candidates[index].risk_points

    selected = [candidates[index] for index in reversed(selected_indices)]
    total_risk = sum(stock.risk_points for stock in selected)
    total_value = sum(stock.momentum_value for stock in selected)

    return PortfolioResult(
        selected=selected,
        total_value=total_value,
        total_risk_points=total_risk,
        capacity_points=capacity_points,
    )

# Comparison baseline algorithm - Greedy
# repeatedly takes the highest value-to-risk stock until the risk budget is exhausted
def solve_knapsack_greedy(
        candidates: Sequence[StockCandidate],
        capacity_points: int,
    ) -> PortfolioResult:

    if capacity_points <= 0:
        raise ValueError("capacity_points must be positive.")

    selected: List[StockCandidate] = []
    total_risk = 0

    ranked = sorted(
        candidates,
        key=lambda stock: (stock.value_to_risk, stock.momentum_value),
        reverse=True,
    )

    # Select stocks one by one as long as they still fit within the risk budget
    for stock in ranked:
        if total_risk + stock.risk_points <= capacity_points:
            selected.append(stock)
            total_risk += stock.risk_points

    return PortfolioResult(
        selected=selected,
        total_value=sum(stock.momentum_value for stock in selected),
        total_risk_points=total_risk,
        capacity_points=capacity_points,
    )

# Create basic summary statistics for the candidate stocks
def summarize_candidates(candidates: Sequence[StockCandidate]) -> dict:
    """
    This function returns:
    1. number of candidates
    2. average momentum
    3. average volatility
    4. average risk points
    """

    if not candidates:
        return {
            "candidate_count": 0,
            "average_momentum": 0.0,
            "average_volatility": 0.0,
            "average_risk_points": 0.0,
        }

    return {
        "candidate_count": len(candidates),
        "average_momentum": sum(stock.momentum_value for stock in candidates) / len(candidates),
        "average_volatility": sum(stock.volatility_20d for stock in candidates) / len(candidates),
        "average_risk_points": sum(stock.risk_points for stock in candidates) / len(candidates),
    }

# converts a portfolio into a list of dictionaries that display cleanly as a table
def portfolio_to_rows(portfolio: PortfolioResult) -> List[dict]:
    rows = []
    for stock in portfolio.selected:
        rows.append(
            {
                "Ticker": stock.ticker,
                "Price": round(stock.price, 2),
                "5-day return": stock.return_5d,
                "20-day return": stock.return_20d,
                "Momentum score": stock.momentum_value,
                "20-day volatility": stock.volatility_20d,
                "Risk points": stock.risk_points,
                "Value per risk point": stock.value_to_risk,
                "Next 20-day return": stock.future_return_20d,
            }
        )
    return rows

# Runs DP and greedy portfolios for several risk budgets, 
# and compares their results in a list of dictionaries
def compare_across_capacities(
        candidates: Sequence[StockCandidate],
        capacities: Iterable[int],
    ) -> List[dict]:

    rows = []
    for capacity in capacities:
        dp_result = solve_knapsack_dp(candidates, capacity)
        greedy_result = solve_knapsack_greedy(candidates, capacity)
        rows.append(
            {
                "Risk budget": capacity,
                "DP stocks": len(dp_result.selected),
                "DP risk used": dp_result.total_risk_points,
                "DP momentum": dp_result.total_value,
                "DP next 20-day avg return": dp_result.average_future_return,
                "Greedy stocks": len(greedy_result.selected),
                "Greedy risk used": greedy_result.total_risk_points,
                "Greedy momentum": greedy_result.total_value,
                "Greedy next 20-day avg return": greedy_result.average_future_return,
                "DP momentum advantage": dp_result.total_value - greedy_result.total_value,
            }
        )
    return rows
