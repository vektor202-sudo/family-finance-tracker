"""Family finance tracker utilities."""

from __future__ import annotations

from typing import Dict

import streamlit as st


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


st.title("Семейный финансовый трекер")

total_income = st.number_input(
    "Общая сумма дохода",
    min_value=0.0,
    step=1000.0,
    format="%.2f",
)

if st.button("Распределить бюджет"):
    distribution = allocate_income(total_income)
    expenses_col, savings_col, investments_col = st.columns(3)

    with expenses_col:
        st.subheader("Расходы 70%")
        st.write(f"{distribution['expenses']:.2f}")

    with savings_col:
        st.subheader("Накопления 10%")
        st.write(f"{distribution['savings']:.2f}")

    with investments_col:
        st.subheader("Инвестиции 20%")
        st.write(f"{distribution['investments']:.2f}")

    st.caption("Данные рассчитаны на основе вашей структуры в docs/data_structure.md")

st.subheader("Добавить новый расход")
with st.form("Добавить новый расход"):
    expense_date = st.date_input("Дата")
    expense_amount = st.number_input(
        "Сумма",
        min_value=0.0,
        step=100.0,
        format="%.2f",
    )
    expense_category = st.selectbox(
        "Категория",
        ["Продукты", "Жилье", "Транспорт", "Развлечения", "Бытовые", "Другое"],
    )
    submit_expense = st.form_submit_button("Сохранить расход")

if submit_expense:
    st.success("Расход сохранен!")
    st.write("Дата:", expense_date)
    st.write("Сумма:", f"{expense_amount:.2f}")
    st.write("Категория:", expense_category)
