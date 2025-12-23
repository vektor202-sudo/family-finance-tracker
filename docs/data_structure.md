# Структура данных проекта
Здесь описана логика хранения информации, предложенная Codex.
```json
{
  "incomes": {
    "husbandSalary": [
      {
        "date": "2024-01-15",
        "amount": 120000,
        "currency": "RUB",
        "note": "January salary"
      }
    ],
    "wifeSalary": [
      {
        "date": "2024-01-20",
        "amount": 110000,
        "currency": "RUB",
        "note": "January salary"
      }
    ],
    "investments": [
      {
        "date": "2024-01-31",
        "amount": 5000,
        "currency": "RUB",
        "source": "dividends",
        "note": "Dividend payout"
      }
    ]
  },
  "expenses": [
    {
      "date": "2024-02-01",
      "amount": 4500,
      "currency": "RUB",
      "category": "groceries",
      "note": "Supermarket"
    }
  ],
  "financialGoals": [
    {
      "id": "goal-1",
      "title": "Emergency fund",
      "targetAmount": 300000,
      "currentAmount": 120000,
      "currency": "RUB",
      "completionPercent": 40
    }
  ]
}
