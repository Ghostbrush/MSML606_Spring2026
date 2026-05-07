# MSML606 Project 2: Budget-Constrained Stock Selection

This project uses a dynamic programming solution to the 0/1 knapsack problem to choose a basket of S&P 500 stocks under a fixed risk budget.

## Files

- `project2.ipynb`: main runnable notebook with explanation, code, results, and charts.
- `portfolio_knapsack.py`: reusable Python functions for loading prices, computing stock features, and solving the knapsack problem.
- `Project2_proposal.ipynb` and `Project2_proposal.pdf`: original proposal files.
- `SP500_Historical_Data.csv`: Kaggle dataset file. This file is large and is intentionally ignored by Git.

## Dataset Setup

Download the S&P 500 historical data CSV from Kaggle:

https://www.kaggle.com/datasets/jacksaleeby/s-and-p500-historical-data

Place the file in this project folder with this exact name:

```text
SP500_Historical_Data.csv
```

## How to Run

Install the notebook dependencies if needed:

```bash
pip install -r requirements.txt
```

Then open and run:

```bash
jupyter notebook project2.ipynb
```

The notebook is designed for a non-CS audience. It explains the stock-selection problem in plain language, shows why 0/1 knapsack fits the problem, compares dynamic programming against a greedy baseline, and includes a simple 20-trading-day holdout check.
