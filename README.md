# Health Insurance Calculator (Flask + Matplotlib)

A small tool to visualize and compare health-insurance plan costs across a range of annual medical spending. It plots each plan’s **total annual cost** (premiums + out-of-pocket, capped by OOP max) and marks **intersection points** where one plan becomes cheaper than another.

## Features

- Piecewise cost model per plan:
  - Premiums (monthly → annual)
  - Deductible
  - Fixed subsidy (flat amount subtracted from post-deductible window)
  - Coinsurance
  - Copay (or use Max OOP if no copay)
  - Out-of-Pocket Max
- Plots multiple plans and marks **intersection** points (where plan A = plan B).
- Simple Flask endpoints (`/`, `/plot`) to render a form and return a PNG plot.

---

## Requirements

- Python 3.9+
- Packages:
  - `flask`
  - `numpy`
  - `matplotlib`
