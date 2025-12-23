"""Family finance tracker utilities."""

from __future__ import annotations

from typing import Dict


def allocate_income(total_income: float) -> Dict[str, float]:
    """Distribute total income into expenses, savings, and investments.

    Rules:
    - 70% to expenses
    - 10% to savings (goals)
    - 20% to investments
    """
    if total_income < 0:
        raise ValueError("total_income must be non-negative")

    expenses = total_income * 0.70
    savings = total_income * 0.10
    investments = total_income * 0.20

    return {
        "expenses": expenses,
        "savings": savings,
        "investments": investments,
    }


if __name__ == "__main__":
    total = 100000
    distribution = allocate_income(total)
    print(f"Общий доход: {total}")
    print("Распределение:")
    print(f"  Расходы (70%): {distribution['expenses']}")
    print(f"  Накопления (10%): {distribution['savings']}")
    print(f"  Инвестиции (20%): {distribution['investments']}")
