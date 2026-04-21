# 🛠️ TOOLS — Finance AI Agent

## 🎯 Purpose

This document defines all tools used by the Finance AI Agent.

Tools enable the agent to:

* Extract data
* Process information
* Perform calculations
* Generate insights

---

## 📄 1. Bank Statement Parser

### Description

Extracts structured transaction data from PDF bank statements.

### Input

* PDF file

### Output

```json
{
  "transactions": [
    {
      "date": "2026-03-01",
      "amount": 500,
      "type": "debit",
      "merchant": "Zomato"
    }
  ]
}
```

### Responsibilities

* Extract tables from PDF
* Normalize data
* Identify transaction fields
* Remove duplicates

---

## 🖼️ 2. Image / Graph Analyzer

### Description

Analyzes Google Pay / UPI transaction graphs and screenshots.

### Input

* Image file

### Output

```json
{
  "insights": {
    "top_category": "Shopping",
    "monthly_spending": 25000
  }
}
```

### Responsibilities

* Interpret charts (bar, pie, trends)
* Extract visible data
* Infer spending patterns
* Avoid guessing unclear values

---

## 📊 3. Expense Categorizer

### Description

Classifies transactions into predefined categories.

### Input

```json
{
  "merchant": "Swiggy",
  "amount": 300
}
```

### Output

```json
{
  "category": "Food"
}
```

### Categories

* Food
* Transport
* Shopping
* Bills
* Subscriptions
* Other

---

## 🧮 4. Financial Calculator

### Description

Computes financial summaries and metrics.

### Input

```json
{
  "transactions": [...]
}
```

### Output

```json
{
  "income": 60000,
  "expenses": 42000,
  "savings": 18000
}
```

### Responsibilities

* Calculate totals
* Compute savings
* Generate category breakdown

---

## 📈 5. Savings Planner

### Description

Generates savings strategies based on financial data.

### Input

```json
{
  "income": 60000,
  "expenses": 42000
}
```

### Output

```json
{
  "suggestions": [
    "Reduce shopping expenses by 20%",
    "Allocate ₹7000 to savings"
  ]
}
```

### Responsibilities

* Apply budgeting rules
* Suggest improvements
* Provide realistic recommendations

---

## 🔮 6. Financial Simulator

### Description

Simulates financial scenarios.

### Input

```json
{
  "purchase_amount": 50000,
  "current_savings": 18000
}
```

### Output

```json
{
  "affordable": false,
  "message": "Purchase not recommended"
}
```

### Responsibilities

* Evaluate affordability
* Predict impact on savings
* Provide decision guidance

---

## 🧩 Tool Usage Rules

* Always use tools for:

  * Data extraction
  * Calculations
  * Simulations

* Do NOT:

  * Guess outputs
  * Skip tool usage when required

---

## 🚀 Summary

These tools form the core functional layer of the Finance AI Agent, enabling it to operate as a **data-driven intelligent system**.

---
