"""Family finance tracker utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd
import plotly.express as px
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

st.sidebar.header("Установка цели")
goal_name = st.sidebar.text_input("Название цели", value="Финансовая подушка")
goal_amount = st.sidebar.number_input(
    "Сумма цели",
    min_value=0.0,
    step=1000.0,
    format="%.2f",
)
goal_saved = st.sidebar.number_input(
    "Уже накоплено",
    min_value=0.0,
    step=500.0,
    format="%.2f",
)
if goal_amount > 0:
    goal_progress = min(goal_saved / goal_amount, 1.0)
else:
    goal_progress = 0.0
goal_percent = goal_progress * 100
st.sidebar.markdown(f"**{goal_name or 'Финансовая цель'}**")
st.sidebar.progress(goal_progress, text=f"Достигнуто: {goal_percent:.1f}%")
st.sidebar.caption(
    f"Накоплено: {goal_saved:.2f} из {goal_amount:.2f}"
    if goal_amount > 0
    else "Введите сумму цели, чтобы увидеть прогресс."
)

main_tab, history_tab, analytics_tab = st.tabs(
    ["Главная", "История расходов", "Аналитика и Цели"]
)

expenses_file = Path(__file__).parent / "expenses.csv"
if expenses_file.exists():
    expenses_df = pd.read_csv(expenses_file)
else:
    expenses_df = pd.DataFrame(columns=["date", "amount", "category"])

with main_tab:
    st.subheader("Планирование бюджета")
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
        new_expense = pd.DataFrame(
            [
                {
                    "date": expense_date,
                    "amount": expense_amount,
                    "category": expense_category,
                }
            ]
        )
        if expenses_file.exists():
            existing_expenses = pd.read_csv(expenses_file)
            updated_expenses = pd.concat(
                [existing_expenses, new_expense],
                ignore_index=True,
            )
        else:
            updated_expenses = new_expense
        updated_expenses.to_csv(expenses_file, index=False)
        expenses_df = updated_expenses
        st.success("Расход сохранен!")
        st.write("Дата:", expense_date)
        st.write("Сумма:", f"{expense_amount:.2f}")
        st.write("Категория:", expense_category)

with history_tab:
    st.subheader("История расходов")
    st.dataframe(expenses_df, use_container_width=True)

with analytics_tab:
    st.subheader("Аналитика расходов")
    if not expenses_df.empty:
        expenses_summary = expenses_df.groupby("category", as_index=False)["amount"].sum()
        pie_chart = px.pie(
            expenses_summary,
            values="amount",
            names="category",
            hole=0.35,
        )
        pie_chart.update_traces(textposition="inside", textinfo="percent+label")
        pie_chart.update_layout(margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(pie_chart, use_container_width=True)
    else:
        st.info("Добавьте расходы, чтобы увидеть аналитику по категориям.")
