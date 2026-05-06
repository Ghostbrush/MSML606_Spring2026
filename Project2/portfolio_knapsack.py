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
        return sum(returns) / len(returns)

