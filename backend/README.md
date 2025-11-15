# PRO-PAD Backend API

FastAPI backend for the PRO-PAD Dashboard. Provides REST API endpoints for statistical modeling, forecasting, and data analysis.

## Features

- **Data Management** - Load and manage historical PAD data
- **Statistical Modeling** - OLS Regression, ARIMA, Exponential Smoothing
- **Projections** - Multi-year forecasting with confidence intervals
- **Analysis** - Sensitivity analysis, decomposition, correlation
- **Audit Trail** - Activity logging and tracking
- **Policy Management** - Settings and targets management

## Tech Stack

- **FastAPI** - Modern Python web framework
- **Pandas** - Data manipulation
- **Statsmodels** - Statistical modeling
- **Uvicorn** - ASGI server

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

Development mode:
```bash
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Data Endpoints (`/api/data`)
- `GET /historical` - Load historical PAD data
- `GET /pkb-inputs` - Load PKB inputs
- `GET /bbnkb-inputs` - Load BBNKB inputs
- `POST /update` - Update data
- `GET /export` - Export data (Excel/CSV)

### Model Endpoints (`/api/model`)
- `POST /ols` - Run OLS regression
- `POST /arima` - Run ARIMA model
- `POST /exp-smoothing` - Run Exponential Smoothing
- `POST /ensemble` - Run ensemble model
- `POST /validate` - Validate model
- `POST /cross-validate` - Cross-validation
- `POST /backtest` - Backtest model

### Projection Endpoints (`/api/projection`)
- `POST /generate` - Generate projections
- `POST /scenarios` - Scenario analysis
- `POST /confidence-intervals` - Calculate confidence intervals

### Analysis Endpoints (`/api/analysis`)
- `POST /sensitivity` - Sensitivity analysis
- `POST /decomposition` - Decomposition analysis
- `POST /correlation` - Correlation matrix
- `POST /stats-summary` - Statistical summary

### Audit Endpoints (`/api/audit`)
- `POST /log` - Log activity
- `GET /trail` - Get audit trail
- `GET /export` - Export audit log

### Policy Endpoints (`/api/policy`)
- `GET /settings` - Get policy settings
- `POST /settings` - Update policy settings
- `GET /targets` - Get PAD targets
- `POST /targets` - Update targets

## Project Structure

```
backend/
├── api/                    # API route handlers
│   ├── data.py            # Data endpoints
│   ├── model.py           # Model endpoints
│   ├── projection.py      # Projection endpoints
│   ├── analysis.py        # Analysis endpoints
│   ├── audit.py           # Audit endpoints
│   └── policy.py          # Policy endpoints
├── models/                # Data models (Pydantic)
├── services/              # Business logic
├── main.py                # FastAPI application
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Development Status

Currently, this is a skeleton API with placeholder endpoints. Each endpoint needs to be implemented with actual business logic from the existing Streamlit utilities.

### TODO
- [ ] Implement OLS regression using statsmodels
- [ ] Implement ARIMA forecasting
- [ ] Implement Exponential Smoothing
- [ ] Implement ensemble model
- [ ] Implement sensitivity analysis
- [ ] Implement decomposition analysis
- [ ] Implement validation metrics
- [ ] Add authentication/authorization
- [ ] Add rate limiting
- [ ] Add caching layer
- [ ] Complete error handling
- [ ] Add comprehensive logging

## CORS Configuration

The API is configured to accept requests from:
- `http://localhost:5173` (Vite dev server)
- `http://localhost:3000` (Alternative React dev server)

Update `main.py` to add additional origins as needed.

## License

© 2024 Bapenda Provinsi Jawa Timur
