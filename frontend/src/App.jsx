import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';

// Pages
import HomePage from './pages/HomePage';
import DatasetsPage from './pages/DatasetsPage';
import PemodelanPage from './pages/PemodelanPage';
import ProyeksiPage from './pages/ProyeksiPage';
import DekomposisiPage from './pages/DekomposisiPage';
import InsightPage from './pages/InsightPage';
import HKPDPage from './pages/HKPDPage';
import ScenarioBuilderPage from './pages/ScenarioBuilderPage';
import DecisionSupportPage from './pages/DecisionSupportPage';
import UICustomizationPage from './pages/UICustomizationPage';
import VariableManagerPage from './pages/VariableManagerPage';
import PolicySettingsPage from './pages/PolicySettingsPage';
import DataEditorPage from './pages/DataEditorPage';
import MetodologiPage from './pages/MetodologiPage';
import AuditPage from './pages/AuditPage';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/datasets" element={<DatasetsPage />} />
          <Route path="/pemodelan" element={<PemodelanPage />} />
          <Route path="/proyeksi" element={<ProyeksiPage />} />
          <Route path="/dekomposisi" element={<DekomposisiPage />} />
          <Route path="/insight" element={<InsightPage />} />
          <Route path="/hkpd" element={<HKPDPage />} />
          <Route path="/scenario-builder" element={<ScenarioBuilderPage />} />
          <Route path="/decision-support" element={<DecisionSupportPage />} />
          <Route path="/ui-customization" element={<UICustomizationPage />} />
          <Route path="/variable-manager" element={<VariableManagerPage />} />
          <Route path="/policy-settings" element={<PolicySettingsPage />} />
          <Route path="/data-editor" element={<DataEditorPage />} />
          <Route path="/metodologi" element={<MetodologiPage />} />
          <Route path="/audit" element={<AuditPage />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
