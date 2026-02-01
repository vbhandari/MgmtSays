import { Card, CardHeader, Button, Input, Alert } from '../components/ui';

export default function Settings() {
  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-500 mt-1">
          Configure your MgmtSays preferences
        </p>
      </div>

      {/* API Configuration */}
      <Card>
        <CardHeader
          title="API Configuration"
          subtitle="Configure external API connections"
        />
        <div className="space-y-4">
          <Input
            label="OpenAI API Key"
            type="password"
            placeholder="sk-..."
            helperText="Required for AI-powered analysis"
          />
          <Input
            label="Anthropic API Key"
            type="password"
            placeholder="sk-ant-..."
            helperText="Alternative LLM provider"
          />
        </div>
      </Card>

      {/* Analysis Settings */}
      <Card>
        <CardHeader
          title="Analysis Settings"
          subtitle="Configure how documents are analyzed"
        />
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Chunk Size
            </label>
            <select className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="500">500 tokens (faster, less context)</option>
              <option value="1000" selected>1000 tokens (balanced)</option>
              <option value="2000">2000 tokens (slower, more context)</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              LLM Model
            </label>
            <select className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="gpt-4o">GPT-4o (recommended)</option>
              <option value="gpt-4o-mini">GPT-4o Mini (faster)</option>
              <option value="claude-3-5-sonnet">Claude 3.5 Sonnet</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Data Management */}
      <Card>
        <CardHeader
          title="Data Management"
          subtitle="Manage your data and storage"
        />
        <div className="space-y-4">
          <Alert type="warning" title="Danger Zone">
            These actions are irreversible. Please proceed with caution.
          </Alert>
          <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
            <div>
              <h4 className="font-medium text-gray-900">Clear Vector Store</h4>
              <p className="text-sm text-gray-500">
                Remove all indexed documents from the vector database
              </p>
            </div>
            <Button variant="outline" size="sm">
              Clear
            </Button>
          </div>
          <div className="flex items-center justify-between p-4 border border-red-200 rounded-lg bg-red-50">
            <div>
              <h4 className="font-medium text-red-900">Delete All Data</h4>
              <p className="text-sm text-red-700">
                Permanently delete all companies, documents, and analysis
              </p>
            </div>
            <Button variant="danger" size="sm">
              Delete All
            </Button>
          </div>
        </div>
      </Card>

      {/* About */}
      <Card>
        <CardHeader title="About" />
        <div className="space-y-2 text-sm text-gray-600">
          <p><strong>MgmtSays</strong> - Management Disclosure Intelligence Platform</p>
          <p>Version: 1.0.0</p>
          <p>
            Extract strategic insights from management disclosures using 
            LlamaIndex for intelligent retrieval and DSPy for structured reasoning.
          </p>
        </div>
      </Card>

      {/* Save button */}
      <div className="flex justify-end">
        <Button>Save Settings</Button>
      </div>
    </div>
  );
}
