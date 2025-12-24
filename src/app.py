"""Family finance tracker utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd
import plotly.express as px
import streamlit as st


def allocate_income(
    total_income: float,
    expenses_percent: float,
    savings_percent: float,
    investments_percent: float,
) -> Dict[str, float]:
    """Distribute total income into expenses, savings, and investments.

    Rules:
    - Percentages are provided by the user and must sum to 100
    """
    if total_income < 0:
        raise ValueError("total_income must be non-negative")
    if (expenses_percent + savings_percent + investments_percent) != 100:
        raise ValueError("Percentages must sum to 100")

    expenses = total_income * expenses_percent / 100
    savings = total_income * savings_percent / 100
    investments = total_income * investments_percent / 100

    return {
        "expenses": expenses,
        "savings": savings,
        "investments": investments,
    }


st.title("Семейный финансовый трекер")

main_tab, history_tab, analytics_tab, goals_tab, income_tab = st.tabs(
    ["Главная", "История расходов", "Аналитика", "Цели", "Доходы"]
)

expenses_file = Path(__file__).parent / "expenses.csv"
goals_file = Path(__file__).parent / "goals.csv"
income_file = Path(__file__).parent / "income.csv"
if expenses_file.exists():
    expenses_df = pd.read_csv(expenses_file)
else:
    expenses_df = pd.DataFrame(columns=["date", "amount", "category"])

if goals_file.exists():
    goals_df = pd.read_csv(goals_file)
else:
    goals_df = pd.DataFrame(columns=["name", "target_amount", "saved_amount"])
    goals_df.to_csv(goals_file, index=False)

if income_file.exists():
    income_df = pd.read_csv(income_file)
else:
    income_df = pd.DataFrame(columns=["month", "year", "amount", "category"])
    income_df.to_csv(income_file, index=False)

with main_tab:
    st.subheader("Планирование бюджета")
    total_income = st.number_input(
        "Общая сумма дохода",
        min_value=0.0,
        step=1000.0,
        format="%.2f",
    )
    st.markdown("#### Проценты распределения")
    expenses_percent = st.slider("Расходы (%)", min_value=0, max_value=100, value=70)
    investments_percent = st.slider(
        "Инвестиции (%)", min_value=0, max_value=100, value=20
    )
    savings_percent = st.slider("Накопления (%)", min_value=0, max_value=100, value=10)
    total_percent = expenses_percent + investments_percent + savings_percent
    if total_percent != 100:
        st.warning(
            f"Сумма процентов должна быть 100%. Сейчас: {total_percent}%."
        )

    if st.button("Распределить бюджет"):
        if total_percent != 100:
            st.error("Исправьте проценты, чтобы они суммировались до 100%.")
            st.stop()
        distribution = allocate_income(
            total_income,
            expenses_percent,
            savings_percent,
            investments_percent,
        )
        expenses_col, savings_col, investments_col = st.columns(3)

        with expenses_col:
            st.subheader(f"Расходы {expenses_percent}%")
            st.write(f"{distribution['expenses']:.2f}")

        with savings_col:
            st.subheader(f"Накопления {savings_percent}%")
            st.write(f"{distribution['savings']:.2f}")

        with investments_col:
            st.subheader(f"Инвестиции {investments_percent}%")
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

with goals_tab:
    st.subheader("Цели")
    with st.form("Добавить цель"):
        goal_name = st.text_input("Название цели")
        goal_target = st.number_input(
            "Необходимая сумма",
            min_value=0.0,
            step=1000.0,
            format="%.2f",
        )
        submit_goal = st.form_submit_button("Сохранить цель")

    if submit_goal:
        new_goal = pd.DataFrame(
            [
                {
                    "name": goal_name,
                    "target_amount": goal_target,
                    "saved_amount": 0.0,
                }
            ]
        )
        updated_goals = pd.concat([goals_df, new_goal], ignore_index=True)
        updated_goals.to_csv(goals_file, index=False)
        goals_df = updated_goals
        st.success("Цель сохранена!")

    if goals_df.empty:
        st.info("Добавьте цели, чтобы видеть прогресс.")
    else:
        st.markdown("#### Список целей")
        for _, goal in goals_df.iterrows():
            goal_title = goal.get("name") or "Цель без названия"
            target_amount = float(goal.get("target_amount", 0.0) or 0.0)
            saved_amount = float(goal.get("saved_amount", 0.0) or 0.0)
            progress = min(saved_amount / target_amount, 1.0) if target_amount > 0 else 0.0
            percent = progress * 100
            with st.container():
                st.markdown(f"**{goal_title}**")
                st.progress(progress, text=f"Достигнуто: {percent:.1f}%")
                st.caption(
                    f"Накоплено: {saved_amount:.2f} из {target_amount:.2f}"
                    if target_amount > 0
                    else "Введите сумму цели, чтобы увидеть прогресс."
                )

with income_tab:
    st.subheader("Планирование доходов")
    income_month = st.selectbox(
        "Месяц",
        [
            "Январь",
            "Февраль",
            "Март",
            "Апрель",
            "Май",
            "Июнь",
            "Июль",
            "Август",
            "Сентябрь",
            "Октябрь",
            "Ноябрь",
            "Декабрь",
        ],
    )
    income_year = st.number_input("Год", min_value=2000, max_value=2100, value=2024)
    with st.form("Добавить доход"):
        income_amount = st.number_input(
            "Сумма",
            min_value=0.0,
            step=1000.0,
            format="%.2f",
        )
        income_category = st.selectbox(
            "Категория",
            ["Зарплата Мужа", "Зарплата Жены", "Инвестиции"],
        )
        submit_income = st.form_submit_button("Сохранить доход")

    if submit_income:
        new_income = pd.DataFrame(
            [
                {
                    "month": income_month,
                    "year": int(income_year),
                    "amount": income_amount,
                    "category": income_category,
                }
            ]
        )
        updated_income = pd.concat([income_df, new_income], ignore_index=True)
        updated_income.to_csv(income_file, index=False)
        income_df = updated_income
        st.success("Доход сохранен!")

    if income_df.empty:
        st.info("Добавьте доходы, чтобы видеть план.")
    else:
        st.markdown("#### План доходов")
        st.dataframe(income_df, use_container_width=True)
