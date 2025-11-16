# PRO-PAD Frontend - React Dashboard

Dashboard Proyeksi PAD (Pendapatan Asli Daerah) Jawa Timur - Migrasi dari Streamlit ke React.

## Tech Stack

- **React 19** - UI Library
- **Vite** - Build tool & dev server
- **TailwindCSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **Recharts** - Chart library
- **TanStack Table** - Data table library
- **Headless UI** - Unstyled UI components
- **Axios** - HTTP client
- **Lucide React** - Icon library

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── charts/         # Recharts wrapper components
│   │   ├── layout/         # Layout components (Sidebar, Header)
│   │   └── ui/             # Reusable UI components
│   ├── pages/              # Page components
│   ├── services/           # API services
│   ├── hooks/              # Custom React hooks
│   ├── utils/              # Utility functions
│   ├── lib/                # Helper libraries
│   ├── contexts/           # React contexts
│   ├── assets/             # Static assets
│   ├── App.jsx             # Main app component
│   ├── main.jsx            # Entry point
│   └── index.css           # Global styles
├── public/                 # Public assets
├── .env.example            # Environment variables template
├── tailwind.config.js      # Tailwind configuration
├── vite.config.js          # Vite configuration
└── package.json            # Dependencies
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python backend API running (see backend setup)

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Update `.env` with your API URL:
```
VITE_API_URL=http://localhost:8000/api
```

### Development

Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Build

Build for production:
```bash
npm run build
```

Preview production build:
```bash
npm run preview
```

## Features

### Completed
- ✅ Home page with dashboard overview
- ✅ Datasets page with data table and charts
- ✅ Responsive layout with sidebar navigation
- ✅ Reusable UI components (Card, Button, Select, DataTable)
- ✅ Chart components (LineChart, BarChart)
- ✅ API service layer
- ✅ Utility functions (formatting, calculations)

### In Progress
- 🔄 Pemodelan (Statistical Modeling) page
- 🔄 Proyeksi (Projection) page
- 🔄 Dekomposisi (Decomposition) page
- 🔄 Backend API integration

### Planned
- 📋 Full feature parity with Streamlit version
- 📋 Advanced charting (Waterfall, Tornado, Heatmap)
- 📋 Scenario builder functionality
- 📋 Decision support system
- 📋 Audit trail
- 📋 Data editor with CRUD operations

## Component Replacement

| Streamlit Widget | React Component |
|-----------------|-----------------|
| st.selectbox() | Select (Headless UI) |
| st.dataframe() | DataTable (TanStack Table) |
| st.plotly_chart() | LineChart/BarChart (Recharts) |
| st.metric() | MetricCard |
| st.button() | Button |
| st.columns() | CSS Grid |

## API Integration

The frontend communicates with a Python backend API. See `/services/api.js` for available endpoints.

## License

© 2024 Bapenda Provinsi Jawa Timur
