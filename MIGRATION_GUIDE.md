# Panduan Migrasi: Streamlit → React

Dokumen ini menjelaskan proses migrasi dashboard PRO-PAD dari Streamlit (Python) ke React modern dengan Vite dan TailwindCSS.

## Daftar Isi

1. [Ringkasan Migrasi](#ringkasan-migrasi)
2. [Arsitektur Baru](#arsitektur-baru)
3. [Setup & Installation](#setup--installation)
4. [Struktur Kode](#struktur-kode)
5. [Mapping Komponen](#mapping-komponen)
6. [API Integration](#api-integration)
7. [Next Steps](#next-steps)

---

## Ringkasan Migrasi

### Yang Sudah Dikerjakan ✅

1. **Frontend React Setup**
   - ✅ React 19 + Vite project structure
   - ✅ TailwindCSS 4.x configuration
   - ✅ React Router untuk navigation
   - ✅ Folder structure yang clean dan modular

2. **Komponen UI**
   - ✅ Layout components (Sidebar, Header, Layout)
   - ✅ UI components (Card, Button, Select, DataTable, MetricCard)
   - ✅ Chart components (LineChart, BarChart)
   - ✅ Utility functions (formatting, calculations)

3. **Pages**
   - ✅ HomePage - Dashboard overview dengan metrics dan charts
   - ✅ DatasetsPage - Data table dengan visualisasi
   - ✅ 13 placeholder pages lainnya (siap untuk implementasi)

4. **Backend API**
   - ✅ FastAPI application structure
   - ✅ 6 router modules (data, model, projection, analysis, audit, policy)
   - ✅ Skeleton endpoints untuk semua fitur utama
   - ✅ CORS configuration untuk React dev server

5. **Infrastructure**
   - ✅ API service layer di React
   - ✅ Environment variables configuration
   - ✅ Build configuration
   - ✅ Documentation (README untuk frontend & backend)

### Yang Perlu Diselesaikan 🔄

1. **Backend Implementation**
   - 🔄 Implementasi OLS Regression endpoint
   - 🔄 Implementasi ARIMA forecasting
   - 🔄 Implementasi Exponential Smoothing
   - 🔄 Implementasi ensemble models
   - 🔄 Implementasi sensitivity analysis
   - 🔄 Implementasi decomposition analysis
   - 🔄 Implementasi validation metrics

2. **Frontend Pages**
   - 🔄 Pemodelan page (statistical modeling)
   - 🔄 Proyeksi page (forecasting)
   - 🔄 Dekomposisi page (decomposition)
   - 🔄 Scenario Builder page
   - 🔄 Decision Support page
   - 🔄 Insight page
   - 🔄 HKPD page
   - 🔄 Variable Manager page
   - 🔄 Policy Settings page
   - 🔄 Data Editor page
   - 🔄 Metodologi page
   - 🔄 Audit page
   - 🔄 UI Customization page

3. **Advanced Features**
   - 🔄 Chart types (Waterfall, Tornado, Heatmap)
   - 🔄 Real-time data updates
   - 🔄 Export functionality (Excel, PDF)
   - 🔄 Audit trail implementation
   - 🔄 User authentication
   - 🔄 Theme customization

---

## Arsitektur Baru

### Arsitektur Lama (Streamlit)

```
Streamlit App (Python)
├── app.py (single process)
├── pages/*.py (15 pages)
├── utils/*.py (utilities)
└── data_loader.py
```

**Karakteristik:**
- Monolithic application
- Server-side rendering
- Session state management
- Built-in widgets
- Automatic rerun

### Arsitektur Baru (React + FastAPI)

```
┌─────────────────────────────────────┐
│         React Frontend              │
│  (Vite + TailwindCSS + Router)     │
│                                     │
│  ├── Components                     │
│  ├── Pages                          │
│  ├── Services (API calls)          │
│  └── Utils                          │
└─────────────────────────────────────┘
                 │
                 │ HTTP/REST
                 ▼
┌─────────────────────────────────────┐
│       FastAPI Backend               │
│  (Python + Pandas + Statsmodels)   │
│                                     │
│  ├── API Routes                     │
│  ├── Models                         │
│  ├── Services                       │
│  └── Utils (reused from Streamlit) │
└─────────────────────────────────────┘
```

**Keuntungan:**
- ✅ Separation of concerns
- ✅ Better scalability
- ✅ Independent deployment
- ✅ Better performance
- ✅ More flexible UI
- ✅ TypeScript support (future)
- ✅ Better testing capabilities
- ✅ Modern development experience

---

## Setup & Installation

### Prerequisites

```bash
# Verifikasi Node.js (18+)
node --version

# Verifikasi Python (3.10+)
python --version
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Update .env with backend URL
# VITE_API_URL=http://localhost:8000/api

# Start development server
npm run dev
```

Frontend akan berjalan di `http://localhost:5173`

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
python main.py

# Or with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend akan berjalan di `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### Running Both

**Terminal 1 (Backend):**
```bash
cd backend
python main.py
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

---

## Struktur Kode

### Frontend Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── charts/
│   │   │   ├── LineChart.jsx        # Recharts line chart
│   │   │   └── BarChart.jsx         # Recharts bar chart
│   │   ├── layout/
│   │   │   ├── Layout.jsx           # Main layout wrapper
│   │   │   ├── Sidebar.jsx          # Navigation sidebar
│   │   │   └── Header.jsx           # Top header
│   │   └── ui/
│   │       ├── Card.jsx             # Card component
│   │       ├── Button.jsx           # Button component
│   │       ├── Select.jsx           # Dropdown (Headless UI)
│   │       ├── DataTable.jsx        # Data table (TanStack)
│   │       └── MetricCard.jsx       # KPI metric card
│   ├── pages/
│   │   ├── HomePage.jsx             # Dashboard home
│   │   ├── DatasetsPage.jsx         # Data viewer
│   │   ├── PemodelanPage.jsx        # Statistical modeling
│   │   ├── ProyeksiPage.jsx         # Projections
│   │   └── ...                      # 11 other pages
│   ├── services/
│   │   └── api.js                   # API service layer
│   ├── lib/
│   │   └── utils.js                 # Utility functions
│   ├── App.jsx                      # Main app component
│   ├── main.jsx                     # Entry point
│   └── index.css                    # Global styles
├── public/                          # Static assets
├── .env.example                     # Environment template
├── tailwind.config.js               # Tailwind config
├── vite.config.js                   # Vite config
└── package.json                     # Dependencies
```

### Backend Structure

```
backend/
├── api/
│   ├── data.py                      # Data endpoints
│   ├── model.py                     # Model endpoints
│   ├── projection.py                # Projection endpoints
│   ├── analysis.py                  # Analysis endpoints
│   ├── audit.py                     # Audit endpoints
│   └── policy.py                    # Policy endpoints
├── models/                          # Pydantic models (future)
├── services/                        # Business logic (future)
├── main.py                          # FastAPI app
├── requirements.txt                 # Python dependencies
└── README.md                        # Backend docs
```

---

## Mapping Komponen

### Widget Replacement

| Streamlit Widget | React Component | Library |
|-----------------|-----------------|---------|
| `st.selectbox()` | `Select` | Headless UI |
| `st.dataframe()` | `DataTable` | TanStack Table |
| `st.plotly_chart()` | `LineChart` / `BarChart` | Recharts |
| `st.metric()` | `MetricCard` | Custom |
| `st.button()` | `Button` | Custom |
| `st.columns()` | CSS Grid | TailwindCSS |
| `st.expander()` | `Disclosure` | Headless UI |
| `st.tabs()` | `Tab` | Headless UI |
| `st.sidebar` | `Sidebar` | Custom |
| `st.markdown()` | JSX / HTML | React |

### State Management

| Streamlit | React |
|-----------|-------|
| `st.session_state` | `useState`, `useContext`, `Redux` |
| `@st.cache_data` | `React Query`, `SWR`, `useMemo` |

### Page Mapping

| Streamlit File | React Component | Status |
|---------------|-----------------|--------|
| `home.py` | `HomePage.jsx` | ✅ Implemented |
| `datasets.py` | `DatasetsPage.jsx` | ✅ Implemented |
| `pemodelan.py` | `PemodelanPage.jsx` | 🔄 Placeholder |
| `proyeksi.py` | `ProyeksiPage.jsx` | 🔄 Placeholder |
| `dekomposisi.py` | `DekomposisiPage.jsx` | 🔄 Placeholder |
| `insight.py` | `InsightPage.jsx` | 🔄 Placeholder |
| `hkpd.py` | `HKPDPage.jsx` | 🔄 Placeholder |
| `scenario_builder.py` | `ScenarioBuilderPage.jsx` | 🔄 Placeholder |
| `decision_support.py` | `DecisionSupportPage.jsx` | 🔄 Placeholder |
| `ui_customization.py` | `UICustomizationPage.jsx` | 🔄 Placeholder |
| `variable_manager.py` | `VariableManagerPage.jsx` | 🔄 Placeholder |
| `policy_settings.py` | `PolicySettingsPage.jsx` | 🔄 Placeholder |
| `data_editor.py` | `DataEditorPage.jsx` | 🔄 Placeholder |
| `metodologi.py` | `MetodologiPage.jsx` | 🔄 Placeholder |
| `audit.py` | `AuditPage.jsx` | 🔄 Placeholder |

---

## API Integration

### Contoh Penggunaan API di React

```javascript
import { dataAPI, modelAPI } from '../services/api';

// Load historical data
const loadData = async () => {
  try {
    const response = await dataAPI.loadHistoricalData();
    setData(response.data.data);
  } catch (error) {
    console.error('Error loading data:', error);
  }
};

// Run OLS regression
const runOLS = async () => {
  try {
    const response = await modelAPI.runOLSRegression({
      response_var: 'PKB',
      predictor_vars: ['PDRB', 'IPM', 'Gini']
    });
    setModelResults(response.data);
  } catch (error) {
    console.error('Error running model:', error);
  }
};
```

### Implementasi Backend Endpoint

Contoh implementasi endpoint OLS di `backend/api/model.py`:

```python
import pandas as pd
import statsmodels.api as sm
from data_loader import load_pad_historis

@router.post("/ols")
async def run_ols_regression(request: OLSRequest):
    try:
        # Load data
        df = load_pad_historis()

        # Prepare data
        y = df[request.response_var]
        X = df[request.predictor_vars]
        X = sm.add_constant(X)

        # Run OLS
        model = sm.OLS(y, X).fit()

        # Return results
        return {
            "success": True,
            "results": {
                "r_squared": model.rsquared,
                "adj_r_squared": model.rsquared_adj,
                "params": model.params.to_dict(),
                "pvalues": model.pvalues.to_dict(),
                "predictions": model.predict().tolist()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Next Steps

### Prioritas Tinggi

1. **Implementasi Backend Endpoints**
   - Mulai dengan endpoint `/api/data/historical` (sudah basic implementation)
   - Implementasi `/api/model/ols` untuk statistical modeling
   - Implementasi `/api/projection/generate` untuk forecasting

2. **Implementasi Pages**
   - **Pemodelan Page**: Form untuk memilih variabel, run OLS/ARIMA, tampilkan hasil
   - **Proyeksi Page**: Generate projections, tampilkan chart dengan confidence intervals
   - **Datasets Page**: Sudah ada, tambahkan fitur filter dan export

3. **Testing**
   - Test setiap endpoint dengan Postman atau cURL
   - Test setiap page di browser
   - Fix bugs yang ditemukan

### Prioritas Sedang

4. **Advanced Charts**
   - Implementasi Waterfall chart untuk decomposition
   - Implementasi Tornado chart untuk sensitivity analysis
   - Implementasi Heatmap untuk correlation

5. **Export Functionality**
   - Implementasi export to Excel
   - Implementasi export to PDF
   - Implementasi export chart sebagai PNG

6. **Data Management**
   - Implementasi CRUD operations di Data Editor
   - Implementasi data validation
   - Implementasi data import

### Prioritas Rendah

7. **Polish & Features**
   - Implementasi theme customization
   - Implementasi user authentication
   - Implementasi real-time updates
   - Implementasi audit trail
   - Add loading states
   - Add error boundaries
   - Add toast notifications

8. **Performance**
   - Code splitting
   - Lazy loading
   - Caching strategies
   - API optimization

---

## Tips & Best Practices

### Frontend

1. **State Management**: Gunakan `useState` untuk local state, `useContext` untuk shared state
2. **Data Fetching**: Gunakan `useEffect` untuk initial load, consider React Query untuk advanced caching
3. **Error Handling**: Selalu wrap API calls dengan try-catch
4. **Loading States**: Tampilkan loading indicator saat fetch data
5. **Responsive Design**: Gunakan TailwindCSS responsive classes (`md:`, `lg:`)

### Backend

1. **Error Handling**: Selalu wrap dengan try-except dan return proper HTTP status codes
2. **Input Validation**: Gunakan Pydantic models untuk request validation
3. **Logging**: Tambahkan logging untuk debugging
4. **Documentation**: Update docstrings untuk setiap endpoint
5. **Testing**: Tulis unit tests untuk business logic

### General

1. **Git Workflow**: Commit frequently dengan clear messages
2. **Code Review**: Review code sebelum merge
3. **Documentation**: Update README saat add new features
4. **Performance**: Monitor bundle size dan API response time

---

## Resources

### React & Vite
- [React Documentation](https://react.dev)
- [Vite Guide](https://vitejs.dev/guide/)
- [React Router](https://reactrouter.com)

### UI Libraries
- [TailwindCSS](https://tailwindcss.com)
- [Headless UI](https://headlessui.com)
- [Recharts](https://recharts.org)
- [TanStack Table](https://tanstack.com/table)

### Backend
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Pydantic](https://docs.pydantic.dev)
- [Statsmodels](https://www.statsmodels.org)

---

## Troubleshooting

### Frontend Issues

**Error: Cannot find module**
```bash
npm install
```

**Error: TailwindCSS not working**
- Check `tailwind.config.js` content paths
- Check `postcss.config.js` has correct plugins
- Restart dev server

**Error: API calls failing**
- Check backend is running
- Check `.env` has correct `VITE_API_URL`
- Check CORS configuration in backend

### Backend Issues

**Error: Module not found**
```bash
pip install -r requirements.txt
```

**Error: CORS issues**
- Check `allow_origins` in `main.py`
- Add frontend URL to allowed origins

**Error: Import errors**
- Check `sys.path.append` in API files
- Check relative imports

---

## Kontribusi

Untuk berkontribusi ke migrasi ini:

1. Pilih task dari TODO list
2. Create branch baru: `git checkout -b feature/task-name`
3. Implementasi fitur
4. Test thoroughly
5. Commit dan push
6. Create pull request

---

## Lisensi

© 2024 Bapenda Provinsi Jawa Timur

---

**Dibuat pada:** November 2024
**Versi:** 1.0.0
**Status:** Migration in Progress
