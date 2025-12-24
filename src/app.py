"""Family finance tracker utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import json
import pandas as pd
import plotly.express as px
import streamlit as st


def load_settings(settings_path: Path) -> Dict[str, int]:
    """Load saved budget settings or return defaults."""
    defaults = {
        "expenses_percent": 70,
        "investments_percent": 20,
        "savings_percent": 10,
    }
    settings = defaults.copy()
    needs_save = False
    if not settings_path.exists():
        needs_save = True
    else:
        try:
            raw_data = json.loads(settings_path.read_text(encoding="utf-8"))
            settings = {
                "expenses_percent": int(
                    raw_data.get("expenses_percent", defaults["expenses_percent"])
                ),
                "investments_percent": int(
                    raw_data.get("investments_percent", defaults["investments_percent"])
                ),
                "savings_percent": int(
                    raw_data.get("savings_percent", defaults["savings_percent"])
                ),
            }
        except (json.JSONDecodeError, TypeError, ValueError):
            settings = defaults.copy()
            needs_save = True
    if sum(settings.values()) != 100:
        settings = defaults.copy()
        needs_save = True
    if needs_save:
        save_settings(settings_path, settings)
    return settings


def save_settings(settings_path: Path, settings: Dict[str, int]) -> None:
    """Persist budget settings to disk."""
    settings_path.write_text(
        json.dumps(settings, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


settings_file = Path(__file__).parent / "settings.json"
default_budget_settings = load_settings(settings_file)

st.set_page_config(page_title="Семейный бюджет", layout="wide")

st.markdown(
    """
    <style>
        .stApp {
            background-color: #f2efe9;
        }
        h1, h2, h3, h4, h5 {
            color: #3b3b3f;
        }
        p, span, div, label {
            color: #4a4a4f;
        }
        .stButton > button {
            background-color: #e0e0d8;
            color: #2f2f33;
            border: none;
        }
        .stButton > button:hover {
            background-color: #d4d4cb;
            color: #2f2f33;
        }
        .goal-card {
            background-color: #ffffff;
            border: 1px solid #e1ded7;
            border-radius: 12px;
            padding: 16px;
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
        }
        .chart-title {
            text-align: center;
            font-size: 28px;
            font-weight: 600;
            margin: 12px 0 16px;
            color: #3b3b3f;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

for key, value in default_budget_settings.items():
    if key not in st.session_state:
        st.session_state[key] = value

MONTH_NAMES = [
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
]

CHART_COLORS = [
    "#5f7c8a",
    "#8aa39b",
    "#b8bfa3",
    "#d4c8b8",
    "#c18b7a",
    "#8c6f6a",
]

INCOME_LEGEND_CATEGORIES = ["Зарплата Мужа", "Зарплата Жены", "Инвестиции"]


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
    ["Главная", "История расходов", "Статистика", "Цели", "Доходы"]
)

expenses_file = Path(__file__).parent / "expenses.csv"
goals_file = Path(__file__).parent / "goals.csv"
income_file = Path(__file__).parent / "income.csv"
if expenses_file.exists():
    expenses_df = pd.read_csv(expenses_file)
else:
    expenses_df = pd.DataFrame(columns=["date", "amount", "category"])

if not expenses_df.empty:
    expenses_df["date"] = pd.to_datetime(expenses_df["date"])
    if "month" not in expenses_df.columns:
        expenses_df["month"] = expenses_df["date"].dt.month.apply(
            lambda month: MONTH_NAMES[month - 1]
        )
    if "year" not in expenses_df.columns:
        expenses_df["year"] = expenses_df["date"].dt.year

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


def update_settings_from_state() -> None:
    save_settings(
        settings_file,
        {
            "expenses_percent": int(st.session_state.get("expenses_percent", 70)),
            "investments_percent": int(st.session_state.get("investments_percent", 20)),
            "savings_percent": int(st.session_state.get("savings_percent", 10)),
        },
    )

with main_tab:
    st.subheader("Планирование бюджета")
    total_income = st.number_input(
        "Общая сумма дохода",
        min_value=0.0,
        step=1000.0,
        format="%.2f",
    )
    st.markdown("#### Проценты распределения")
    expenses_percent = st.slider(
        "Расходы (%)",
        min_value=0,
        max_value=100,
        value=int(st.session_state["expenses_percent"]),
        key="expenses_percent",
        on_change=update_settings_from_state,
    )
    investments_percent = st.slider(
        "Инвестиции (%)",
        min_value=0,
        max_value=100,
        value=int(st.session_state["investments_percent"]),
        key="investments_percent",
        on_change=update_settings_from_state,
    )
    savings_percent = st.slider(
        "Накопления (%)",
        min_value=0,
        max_value=100,
        value=int(st.session_state["savings_percent"]),
        key="savings_percent",
        on_change=update_settings_from_state,
    )
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
        save_settings(
            settings_file,
            {
                "expenses_percent": int(expenses_percent),
                "investments_percent": int(investments_percent),
                "savings_percent": int(savings_percent),
            },
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
        total_spent = float(expenses_df["amount"].sum()) if not expenses_df.empty else 0.0
        expenses_limit = distribution["expenses"]
        if total_spent > expenses_limit:
            indicator = (
                f"<span style='color:#c43d3d;'>Потрачено {total_spent:.2f} "
                f"из {expenses_limit:.2f}</span>"
            )
        else:
            indicator = f"Потрачено {total_spent:.2f} из {expenses_limit:.2f}"
        st.markdown(indicator, unsafe_allow_html=True)

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
        expense_month_number = pd.Timestamp(expense_date).month
        expense_month = MONTH_NAMES[expense_month_number - 1]
        expense_year = pd.Timestamp(expense_date).year
        new_expense = pd.DataFrame(
            [
                {
                    "date": expense_date,
                    "amount": expense_amount,
                    "category": expense_category,
                    "month": expense_month,
                    "year": expense_year,
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
    if st.button("Отменить последнюю запись", key="undo_last_expense"):
        if expenses_df.empty:
            st.info("Нет расходов для удаления.")
        else:
            updated_expenses = expenses_df.iloc[:-1].copy()
            updated_expenses.to_csv(expenses_file, index=False)
            expenses_df = updated_expenses
            st.success("Последняя запись о расходе удалена.")

with history_tab:
    st.subheader("История расходов")
    if expenses_df.empty:
        st.info("Добавьте расходы, чтобы увидеть историю.")
    else:
        expenses_view = expenses_df.copy()
        expenses_view["date"] = pd.to_datetime(expenses_view["date"])
        expenses_view["month"] = expenses_view["month"].fillna(
            expenses_view["date"].dt.month.apply(lambda month: MONTH_NAMES[month - 1])
        )
        expenses_view["year"] = expenses_view["year"].fillna(
            expenses_view["date"].dt.year
        )
        expenses_view = expenses_view.sort_values(["year", "date"], ascending=False)
        month_groups = (
            expenses_view.groupby(["year", "month"], sort=False)
        )
        for (year, month), group in month_groups:
            st.subheader(f"{month} {int(year)}")
            editable_group = group[["date", "amount", "category"]].copy()
            editable_group["Удалить"] = False
            updated_group = st.data_editor(
                editable_group,
                use_container_width=True,
                hide_index=True,
                key=f"expenses_editor_{year}_{month}",
            )
            if st.button("Удалить выбранные", key=f"delete_{year}_{month}"):
                delete_mask = updated_group["Удалить"]
                remaining_group = updated_group[~delete_mask].drop(columns=["Удалить"])
                remaining_expenses = expenses_view.drop(group.index)
                merged_remaining = pd.concat(
                    [remaining_group, remaining_expenses],
                    ignore_index=True,
                )
                merged_remaining = merged_remaining.drop(
                    columns=["month", "year"], errors="ignore"
                )
                merged_remaining.to_csv(expenses_file, index=False)
                expenses_df = merged_remaining
                st.success("Выбранные расходы удалены.")
            st.divider()

with analytics_tab:
    st.subheader("Статистика")
    month_lookup = {name: idx + 1 for idx, name in enumerate(MONTH_NAMES)}
    income_view = income_df.copy()
    if not income_view.empty:
        income_view["month_number"] = income_view["month"].map(month_lookup)
        income_view["year"] = income_view["year"].astype(int)
        income_view = income_view.loc[
            income_view["category"].isin(INCOME_LEGEND_CATEGORIES)
        ]

    if expenses_df.empty or "date" not in expenses_df.columns:
        expenses_view = pd.DataFrame(
            columns=["date", "amount", "category", "month_number"]
        )
    else:
        expenses_view = expenses_df.copy()
        expenses_view["date"] = pd.to_datetime(expenses_view["date"], errors="coerce")
        expenses_view = expenses_view.dropna(subset=["date"])
        expenses_view["month_number"] = expenses_view["date"].dt.month
        expenses_view["year"] = expenses_view["date"].dt.year

    income_summary = (
        income_view.groupby(["year", "month_number"], as_index=False)["amount"].sum()
        if not income_view.empty
        else pd.DataFrame(columns=["year", "month_number", "amount"])
    ).rename(columns={"amount": "income"})

    expenses_summary = (
        expenses_view.groupby(["year", "month_number"], as_index=False)["amount"].sum()
        if not expenses_view.empty
        else pd.DataFrame(columns=["year", "month_number", "amount"])
    ).rename(columns={"amount": "expenses"})

    monthly_summary = pd.merge(
        income_summary,
        expenses_summary,
        on=["year", "month_number"],
        how="outer",
    ).fillna(0)
    if not monthly_summary.empty:
        monthly_summary = monthly_summary.dropna(subset=["month_number"])
        monthly_summary = monthly_summary.sort_values(["year", "month_number"])
        latest_period = monthly_summary.iloc[-1]
        expense_limit = latest_period["income"] * expenses_percent / 100
        limit_left = expense_limit - latest_period["expenses"]
        st.metric(
            "Остаток лимита на месяц",
            f"{limit_left:.2f}",
            help="Доходы * %Расходов - Реальные траты",
        )

    if not income_view.empty:
        income_by_category = (
            income_view.groupby(["year", "month_number", "category"], as_index=False)[
                "amount"
            ].sum()
        )
        income_by_category["month_label"] = income_by_category.apply(
            lambda row: f"{MONTH_NAMES[int(row['month_number']) - 1]} {int(row['year'])}",
            axis=1,
        )
        income_by_category = income_by_category.sort_values(["year", "month_number"])
        st.markdown(
            "<div class='chart-title'>Учет доходов</div>",
            unsafe_allow_html=True,
        )
        income_chart = px.line(
            income_by_category,
            x="month_label",
            y="amount",
            color="category",
            markers=True,
            color_discrete_sequence=CHART_COLORS,
            labels={"amount": "Сумма", "month_label": "Месяц", "category": "Категория"},
            category_orders={"category": INCOME_LEGEND_CATEGORIES},
        )
        income_chart.update_layout(margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(income_chart, use_container_width=True)
    else:
        st.info("Данных пока нет")

    if not expenses_view.empty:
        expenses_summary = expenses_view.groupby("category", as_index=False)["amount"].sum()
        st.markdown(
            "<div class='chart-title'>Учет расходов за месяц</div>",
            unsafe_allow_html=True,
        )
        pie_chart = px.pie(
            expenses_summary,
            values="amount",
            names="category",
            hole=0.35,
            color_discrete_sequence=CHART_COLORS,
        )
        pie_chart.update_traces(textposition="inside", textinfo="percent+label")
        pie_chart.update_layout(margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(pie_chart, use_container_width=True)

        latest_year = int(expenses_view["date"].dt.year.max())
        yearly_expenses = (
            expenses_view.loc[expenses_view["date"].dt.year == latest_year]
            .groupby(expenses_view["date"].dt.month, as_index=False)["amount"]
            .sum()
            .rename(columns={"date": "month_number", "amount": "total"})
        )
        all_months = pd.DataFrame({"month_number": range(1, 13)})
        yearly_expenses = all_months.merge(yearly_expenses, on="month_number", how="left")
        yearly_expenses["total"] = yearly_expenses["total"].fillna(0)
        yearly_expenses["month"] = yearly_expenses["month_number"].apply(
            lambda month: MONTH_NAMES[int(month) - 1]
        )
        st.markdown(
            "<div class='chart-title'>Динамика за год</div>",
            unsafe_allow_html=True,
        )
        yearly_chart = px.bar(
            yearly_expenses,
            x="month",
            y="total",
            color_discrete_sequence=[CHART_COLORS[0]],
            labels={"total": "Сумма", "month": "Месяц"},
        )
        yearly_chart.update_layout(margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(yearly_chart, use_container_width=True)
    else:
        st.info("Данных пока нет")

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
        savings_income_total = 0.0
        if not income_df.empty:
            savings_income_total = float(
                income_df.loc[income_df["category"] == "Накопления", "amount"].sum()
            )
        allocation_per_goal = (
            savings_income_total / len(goals_df.index) if len(goals_df.index) else 0.0
        )
        for _, goal in goals_df.iterrows():
            goal_title = goal.get("name") or "Цель без названия"
            target_amount = float(goal.get("target_amount", 0.0) or 0.0)
            manual_saved = float(goal.get("saved_amount", 0.0) or 0.0)
            allocated_saved = manual_saved + allocation_per_goal
            progress = (
                min(allocated_saved / target_amount, 1.0) if target_amount > 0 else 0.0
            )
            percent = progress * 100
            with st.container():
                st.markdown(
                    f"<div class='goal-card'><strong>{goal_title}</strong>",
                    unsafe_allow_html=True,
                )
                st.progress(progress, text=f"Достигнуто: {percent:.1f}%")
                st.caption(
                    f"Накоплено: {allocated_saved:.2f} из {target_amount:.2f}"
                    if target_amount > 0
                    else "Введите сумму цели, чтобы увидеть прогресс."
                )
                if savings_income_total > 0:
                    st.caption(
                        f"Авто-накопления распределены: {allocation_per_goal:.2f}"
                    )
                st.markdown("</div>", unsafe_allow_html=True)

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
            ["Зарплата Мужа", "Зарплата Жены", "Инвестиции", "Накопления"],
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

    if st.button("Отменить последнюю запись", key="undo_last_income"):
        if income_df.empty:
            st.info("Нет доходов для удаления.")
        else:
            updated_income = income_df.iloc[:-1].copy()
            updated_income.to_csv(income_file, index=False)
            income_df = updated_income
            st.success("Последняя запись о доходе удалена.")

    if income_df.empty:
        st.info("Добавьте доходы, чтобы видеть план.")
    else:
        st.markdown("#### План доходов")
        income_view = income_df.copy()
        income_view["month_number"] = income_view["month"].map(
            {name: idx + 1 for idx, name in enumerate(MONTH_NAMES)}
        )
        income_view["year"] = income_view["year"].astype(int)
        income_view = income_view.sort_values(
            ["year", "month_number"], ascending=False
        )
        income_groups = income_view.groupby(["year", "month"], sort=False)
        for (year, month), group in income_groups:
            st.subheader(f"{month} {int(year)}")
            st.dataframe(
                group[["amount", "category"]],
                use_container_width=True,
                hide_index=True,
            )
            st.divider()
