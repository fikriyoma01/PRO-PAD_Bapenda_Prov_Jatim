import { useState, useEffect } from 'react';
import { Settings, Palette, Type, Layout, Save, RotateCcw, Sun, Moon, Monitor, CheckCircle, AlertCircle } from 'lucide-react';
import { Card } from '../components/ui/Card';
import Button from '../components/ui/Button';

const COLOR_THEMES = [
  { id: 'default', name: 'Default', primary: '#0891b2', secondary: '#06b6d4' },
  { id: 'blue', name: 'Ocean Blue', primary: '#3b82f6', secondary: '#60a5fa' },
  { id: 'purple', name: 'Royal Purple', primary: '#8b5cf6', secondary: '#a78bfa' },
  { id: 'green', name: 'Forest Green', primary: '#10b981', secondary: '#34d399' },
  { id: 'red', name: 'Ruby Red', primary: '#ef4444', secondary: '#f87171' },
  { id: 'orange', name: 'Sunset Orange', primary: '#f59e0b', secondary: '#fbbf24' }
];

const FONT_OPTIONS = [
  { id: 'inter', name: 'Inter', family: 'Inter, sans-serif' },
  { id: 'roboto', name: 'Roboto', family: 'Roboto, sans-serif' },
  { id: 'poppins', name: 'Poppins', family: 'Poppins, sans-serif' },
  { id: 'system', name: 'System Default', family: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif' }
];

const DEFAULT_SETTINGS = {
  theme: 'light',
  colorTheme: 'default',
  fontSize: 16,
  fontFamily: 'inter',
  sidebarCollapsed: false,
  compactMode: false,
  showAnimations: true,
  borderRadius: 8
};

export default function UICustomizationPage() {
  const [settings, setSettings] = useState(DEFAULT_SETTINGS);
  const [hasChanges, setHasChanges] = useState(false);
  const [saveStatus, setSaveStatus] = useState(null);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = () => {
    const saved = localStorage.getItem('ui_settings');
    if (saved) {
      setSettings(JSON.parse(saved));
    }
  };

  const handleSave = () => {
    try {
      localStorage.setItem('ui_settings', JSON.stringify(settings));
      setSaveStatus('success');
      setHasChanges(false);
      setTimeout(() => setSaveStatus(null), 3000);
    } catch (err) {
      console.error('Error saving:', err);
      setSaveStatus('error');
      setTimeout(() => setSaveStatus(null), 3000);
    }
  };

  const handleReset = () => {
    setSettings(DEFAULT_SETTINGS);
    setHasChanges(true);
  };

  const updateSetting = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }));
    setHasChanges(true);
  };

  const selectedColorTheme = COLOR_THEMES.find(t => t.id === settings.colorTheme) || COLOR_THEMES[0];
  const selectedFont = FONT_OPTIONS.find(f => f.id === settings.fontFamily) || FONT_OPTIONS[0];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Settings size={32} className="text-purple-600" />
          <div>
            <h1 className="text-3xl font-bold text-gray-900">UI Customization</h1>
            <p className="text-gray-600 mt-2">Personalisasi tampilan dashboard Anda</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleReset}>
            <RotateCcw size={16} className="mr-2" />
            Reset
          </Button>
          <Button onClick={handleSave} disabled={!hasChanges}>
            <Save size={16} className="mr-2" />
            {saveStatus === 'success' ? 'Saved!' : 'Save Settings'}
          </Button>
        </div>
      </div>

      {/* Status Banners */}
      {saveStatus === 'success' && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center gap-3">
          <CheckCircle className="text-green-600" size={24} />
          <p className="text-green-800 font-medium">UI preferences berhasil disimpan!</p>
        </div>
      )}

      {hasChanges && !saveStatus && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-center gap-3">
          <AlertCircle className="text-yellow-600" size={24} />
          <p className="text-yellow-800 font-medium">Ada perubahan yang belum disimpan</p>
        </div>
      )}

      {/* Theme Mode */}
      <Card>
        <div className="flex items-center gap-3 mb-4">
          <Sun size={24} className="text-purple-600" />
          <h2 className="text-xl font-semibold">Theme Mode</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => updateSetting('theme', 'light')}
            className={`p-4 border-2 rounded-lg transition-all ${
              settings.theme === 'light'
                ? 'border-purple-600 bg-purple-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <Sun size={32} className={`mx-auto mb-2 ${settings.theme === 'light' ? 'text-purple-600' : 'text-gray-400'}`} />
            <p className="font-medium text-gray-900">Light</p>
            <p className="text-sm text-gray-600">Tema terang</p>
          </button>

          <button
            onClick={() => updateSetting('theme', 'dark')}
            className={`p-4 border-2 rounded-lg transition-all ${
              settings.theme === 'dark'
                ? 'border-purple-600 bg-purple-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <Moon size={32} className={`mx-auto mb-2 ${settings.theme === 'dark' ? 'text-purple-600' : 'text-gray-400'}`} />
            <p className="font-medium text-gray-900">Dark</p>
            <p className="text-sm text-gray-600">Tema gelap</p>
          </button>

          <button
            onClick={() => updateSetting('theme', 'auto')}
            className={`p-4 border-2 rounded-lg transition-all ${
              settings.theme === 'auto'
                ? 'border-purple-600 bg-purple-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <Monitor size={32} className={`mx-auto mb-2 ${settings.theme === 'auto' ? 'text-purple-600' : 'text-gray-400'}`} />
            <p className="font-medium text-gray-900">Auto</p>
            <p className="text-sm text-gray-600">Ikuti sistem</p>
          </button>
        </div>
      </Card>

      {/* Color Theme */}
      <Card>
        <div className="flex items-center gap-3 mb-4">
          <Palette size={24} className="text-purple-600" />
          <h2 className="text-xl font-semibold">Color Theme</h2>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {COLOR_THEMES.map(theme => (
            <button
              key={theme.id}
              onClick={() => updateSetting('colorTheme', theme.id)}
              className={`p-4 border-2 rounded-lg transition-all ${
                settings.colorTheme === theme.id
                  ? 'border-purple-600 bg-purple-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex gap-1 mb-2">
                <div
                  className="w-6 h-6 rounded"
                  style={{ backgroundColor: theme.primary }}
                />
                <div
                  className="w-6 h-6 rounded"
                  style={{ backgroundColor: theme.secondary }}
                />
              </div>
              <p className="text-sm font-medium text-gray-900">{theme.name}</p>
            </button>
          ))}
        </div>
        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
          <p className="text-sm text-gray-600 mb-2">Preview:</p>
          <div className="flex gap-2">
            <div
              className="px-4 py-2 rounded-lg text-white font-medium"
              style={{ backgroundColor: selectedColorTheme.primary }}
            >
              Primary Button
            </div>
            <div
              className="px-4 py-2 rounded-lg text-white font-medium"
              style={{ backgroundColor: selectedColorTheme.secondary }}
            >
              Secondary Button
            </div>
          </div>
        </div>
      </Card>

      {/* Typography */}
      <Card>
        <div className="flex items-center gap-3 mb-4">
          <Type size={24} className="text-purple-600" />
          <h2 className="text-xl font-semibold">Typography</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Font Family
            </label>
            <select
              value={settings.fontFamily}
              onChange={(e) => updateSetting('fontFamily', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
            >
              {FONT_OPTIONS.map(font => (
                <option key={font.id} value={font.id}>{font.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Base Font Size: {settings.fontSize}px
            </label>
            <input
              type="range"
              min="12"
              max="20"
              value={settings.fontSize}
              onChange={(e) => updateSetting('fontSize', Number(e.target.value))}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>12px</span>
              <span>16px</span>
              <span>20px</span>
            </div>
          </div>
        </div>

        <div className="mt-4 p-4 bg-gray-50 rounded-lg" style={{ fontFamily: selectedFont.family, fontSize: `${settings.fontSize}px` }}>
          <p className="text-gray-600 mb-1">Preview Text:</p>
          <h3 className="text-2xl font-bold text-gray-900 mb-2">Quick Brown Fox</h3>
          <p className="text-gray-700">The quick brown fox jumps over the lazy dog. 0123456789</p>
        </div>
      </Card>

      {/* Layout Settings */}
      <Card>
        <div className="flex items-center gap-3 mb-4">
          <Layout size={24} className="text-purple-600" />
          <h2 className="text-xl font-semibold">Layout & Spacing</h2>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
            <div>
              <h3 className="font-semibold text-gray-900">Compact Mode</h3>
              <p className="text-sm text-gray-600">Reduce spacing and padding untuk tampilan lebih padat</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.compactMode}
                onChange={(e) => updateSetting('compactMode', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
            </label>
          </div>

          <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
            <div>
              <h3 className="font-semibold text-gray-900">Sidebar Collapsed</h3>
              <p className="text-sm text-gray-600">Sidebar dalam mode collapsed secara default</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.sidebarCollapsed}
                onChange={(e) => updateSetting('sidebarCollapsed', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
            </label>
          </div>

          <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
            <div>
              <h3 className="font-semibold text-gray-900">Animations</h3>
              <p className="text-sm text-gray-600">Aktifkan transisi dan animasi UI</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.showAnimations}
                onChange={(e) => updateSetting('showAnimations', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Border Radius: {settings.borderRadius}px
            </label>
            <input
              type="range"
              min="0"
              max="20"
              value={settings.borderRadius}
              onChange={(e) => updateSetting('borderRadius', Number(e.target.value))}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>Sharp (0px)</span>
              <span>Default (8px)</span>
              <span>Rounded (20px)</span>
            </div>
          </div>
        </div>
      </Card>

      {/* Preview Card */}
      <Card>
        <h2 className="text-xl font-semibold mb-4">Live Preview</h2>
        <div
          className="p-6 border-2 border-gray-200 rounded-lg"
          style={{
            fontFamily: selectedFont.family,
            fontSize: `${settings.fontSize}px`,
            borderRadius: `${settings.borderRadius}px`
          }}
        >
          <h3 className="text-2xl font-bold mb-3" style={{ color: selectedColorTheme.primary }}>
            Sample Dashboard Card
          </h3>
          <p className="text-gray-700 mb-4">
            This is a preview of how your dashboard will look with the current settings.
            All typography, colors, and spacing will be applied accordingly.
          </p>
          <div className="flex gap-2">
            <button
              className="px-4 py-2 text-white rounded-lg font-medium transition-all"
              style={{
                backgroundColor: selectedColorTheme.primary,
                borderRadius: `${settings.borderRadius}px`
              }}
            >
              Primary Action
            </button>
            <button
              className="px-4 py-2 text-white rounded-lg font-medium transition-all"
              style={{
                backgroundColor: selectedColorTheme.secondary,
                borderRadius: `${settings.borderRadius}px`
              }}
            >
              Secondary Action
            </button>
          </div>
        </div>
      </Card>

      {/* Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-sm text-blue-800">
          <strong>Note:</strong> Beberapa perubahan mungkin memerlukan refresh halaman untuk diterapkan sepenuhnya.
          Pengaturan akan tersimpan di browser Anda.
        </p>
      </div>
    </div>
  );
}
