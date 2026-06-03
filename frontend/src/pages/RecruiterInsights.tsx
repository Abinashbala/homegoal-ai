import { useEffect, useState } from 'react';
import { PlannerAPI } from '../api/client';
import { Loader2, Database, TrendingUp, ShieldCheck } from 'lucide-react';
import { ModelComparisonResponse } from '../types';

export default function RecruiterInsights() {
  const [metrics, setMetrics] = useState<ModelComparisonResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadMetrics() {
      try {
        const res = await PlannerAPI.getModelComparison();
        setMetrics(res);
      } catch (e) {
        console.error('Failed to load model metrics', e);
      } finally {
        setLoading(false);
      }
    }
    loadMetrics();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader2 className="animate-spin text-brand-600 w-10 h-10" />
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12 text-center">
        <h2 className="text-2xl font-bold text-gray-900">Backend Unreachable</h2>
        <p className="mt-2 text-gray-500">Could not fetch model metrics from the FastAPI backend. Make sure the server is running.</p>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 w-full pb-24">
      <div className="mb-10 text-center">
        <span className="bg-brand-100 text-brand-800 text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider mb-4 inline-block">For Reviewers</span>
        <h1 className="text-4xl font-bold text-gray-900 tracking-tight">Project Architecture & Models</h1>
        <p className="text-gray-500 mt-3 max-w-2xl mx-auto text-lg">
          A behind-the-scenes look at the data engineering, machine learning validation, and business logic powering HomeGoal AI.
        </p>
      </div>

      {/* Section 1: Architecture Diagram */}
      <div className="card p-8 mb-8 bg-gray-900 text-white border-0 shadow-2xl">
        <h2 className="text-2xl font-bold mb-6 flex items-center gap-3"><Database className="text-brand-400"/> System Architecture</h2>
        <div className="flex flex-col md:flex-row items-stretch justify-between gap-4 text-center">
          <div className="bg-gray-800 p-4 rounded-lg flex-1 border border-gray-700 shadow-inner">
            <h3 className="font-bold text-brand-300 mb-2">1. User UI</h3>
            <p className="text-sm text-gray-400">React + Tailwind<br/>Vite + Context API</p>
          </div>
          <div className="hidden md:flex items-center justify-center text-gray-500">→</div>
          <div className="bg-gray-800 p-4 rounded-lg flex-1 border border-gray-700 shadow-inner">
            <h3 className="font-bold text-brand-300 mb-2">2. API Gateway</h3>
            <p className="text-sm text-gray-400">FastAPI<br/>Pydantic Validation</p>
          </div>
          <div className="hidden md:flex items-center justify-center text-gray-500">→</div>
          <div className="bg-gray-800 p-4 rounded-lg flex-1 border border-gray-700 shadow-inner">
            <h3 className="font-bold text-brand-300 mb-2">3. Deterministic Engines</h3>
            <p className="text-sm text-gray-400">Scenario Engine<br/>Stress Score Engine</p>
          </div>
        </div>
        <p className="text-gray-400 mt-6 text-sm leading-relaxed text-center">
          <strong>Design Decision:</strong> Machine Learning models (Prophet, XGBoost) were utilized in Phase 5 to <em>validate</em> the CAGR boundaries offline. Production relies on a deterministic scenario engine to ensure high interpretability and exact adherence to defined conservative/expected/optimistic bands.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Section 2: HPI Validation */}
        <div className="card p-6">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2"><TrendingUp className="text-brand-600"/> Housing Model (HPI) Validation</h2>
          <p className="text-sm text-gray-600 mb-4">
            Tested on NHB HPI data. The structural break of the 2022-2025 boom made complex models (Prophet/XGBoost) overfit to slow pre-COVID growth. <strong>Exponential Trend</strong> provided the best predictive performance.
          </p>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="p-3">Model</th>
                  <th className="p-3">MAE</th>
                  <th className="p-3">MAPE</th>
                </tr>
              </thead>
              <tbody>
                {metrics.hpi.all_models.map((m: any, i: number) => (
                  <tr key={i} className={m.model === metrics.hpi.best_model.model ? "bg-green-50 font-medium text-green-800" : "border-b border-gray-50"}>
                    <td className="p-3">{m.model} {m.model === metrics.hpi.best_model.model && '🏆'}</td>
                    <td className="p-3">{m.MAE?.toFixed(2) || 'N/A'}</td>
                    <td className="p-3">{m.MAPE?.toFixed(2) || 'N/A'}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-4 bg-gray-50 p-3 rounded text-sm text-gray-700 border border-gray-100">
            <strong>Production Implication:</strong> Model validates the Expected CAGR scenario of {metrics.scenario_parameters.hpi.expected_cagr_pct}%.
          </div>
        </div>

        {/* Section 3: FX Validation */}
        <div className="card p-6">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2"><TrendingUp className="text-brand-600"/> Currency Model (FX) Validation</h2>
          <p className="text-sm text-gray-600 mb-4">
            Tested on monthly AED/INR rates. <strong>Prophet</strong> clearly outperformed linear and exponential approaches by detecting historical changepoints (e.g. 2017 dip).
          </p>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="p-3">Model</th>
                  <th className="p-3">MAE</th>
                  <th className="p-3">MAPE</th>
                </tr>
              </thead>
              <tbody>
                {metrics.fx.all_models.map((m: any, i: number) => (
                  <tr key={i} className={m.model === metrics.fx.best_model.model ? "bg-green-50 font-medium text-green-800" : "border-b border-gray-50"}>
                    <td className="p-3">{m.model} {m.model === metrics.fx.best_model.model && '🏆'}</td>
                    <td className="p-3">{m.MAE?.toFixed(3) || 'N/A'}</td>
                    <td className="p-3">{m.MAPE?.toFixed(2) || 'N/A'}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-4 bg-gray-50 p-3 rounded text-sm text-gray-700 border border-gray-100">
             <strong>Production Implication:</strong> Prophet projection validates the expected full-period CAGR of {metrics.scenario_parameters.fx.expected_cagr_pct}%.
          </div>
        </div>
      </div>

      {/* Section 4: Stress Score Engine */}
      <div className="card p-6">
        <h2 className="text-xl font-bold mb-4 flex items-center gap-2"><ShieldCheck className="text-brand-600"/> Deterministic Stress Score Engine</h2>
        <p className="text-gray-600 mb-4">
          A purely rule-based risk classification engine mapping inputs to a 0-100 stress signal. 
          Allows users to see exactly why their goal is classified as "Safe" vs "Risky".
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-50 p-4 rounded border border-gray-100">
            <h3 className="font-bold text-gray-800 mb-1">1. Goal Gap Ratio (40%)</h3>
            <p className="text-xs text-gray-500">Measures the absolute shortfall relative to the future property cost. Caps at 1.0.</p>
          </div>
          <div className="bg-gray-50 p-4 rounded border border-gray-100">
            <h3 className="font-bold text-gray-800 mb-1">2. Expense Burden (30%)</h3>
            <p className="text-xs text-gray-500">Measures current lifestyle lock-in. Penalizes ratios over 70% of salary.</p>
          </div>
          <div className="bg-gray-50 p-4 rounded border border-gray-100">
            <h3 className="font-bold text-gray-800 mb-1">3. Coverage Shortfall (30%)</h3>
            <p className="text-xs text-gray-500">Inverse of wealth coverage. Rewards high initial wealth accumulations.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
