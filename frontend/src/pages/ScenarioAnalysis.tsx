import { useEffect, useState } from 'react';
import { usePlanner } from '../context/PlannerContext';
import { Navigate } from 'react-router-dom';
import Plot from 'react-plotly.js';
import { Loader2 } from 'lucide-react';
import { formatCurrency } from '../utils/format';

export default function ScenarioAnalysis() {
  const { forecastResult } = usePlanner();
  const [scenarioData, setScenarioData] = useState<any>(null);

  useEffect(() => {
    // We already have the forecastResult which contains conservative, expected, and optimistic scenarios
    // So we don't necessarily need to hit /scenarios unless we want to, 
    // but the backend returns exactly what we need in the forecast response.
    if (forecastResult) {
      setScenarioData({
        conservative: forecastResult.conservative,
        expected: forecastResult.expected,
        optimistic: forecastResult.optimistic
      });
    }
  }, [forecastResult]);

  if (!forecastResult) {
    return <Navigate to="/planner" />;
  }

  if (!scenarioData) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader2 className="animate-spin text-brand-600 w-10 h-10" />
      </div>
    );
  }

  const { conservative: c, expected: e, optimistic: o } = scenarioData;

  const getBarColor = (gap: number) => gap > 0 ? '#E74C3C' : '#27AE60'; // Red for shortfall, Green for surplus

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 w-full">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Scenario Comparison</h1>
        <p className="text-gray-500 mt-1">Comparing Conservative, Expected, and Optimistic projections side-by-side.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        
        {/* Chart 1: Wealth vs Property Cost */}
        <div className="card p-4">
          <h2 className="text-lg font-bold mb-4 ml-4">Real Wealth vs. Property Cost</h2>
          <Plot
            data={[
              {
                x: ['Conservative', 'Expected', 'Optimistic'],
                y: [c.wealth.real_wealth_inr, e.wealth.real_wealth_inr, o.wealth.real_wealth_inr],
                type: 'bar',
                name: 'Real Wealth (INR)',
                marker: { color: '#1B4F72' }
              },
              {
                x: ['Conservative', 'Expected', 'Optimistic'],
                y: [c.property.future_value_inr, e.property.future_value_inr, o.property.future_value_inr],
                type: 'bar',
                name: 'Property Cost (INR)',
                marker: { color: '#BDC3C7' }
              }
            ]}
            layout={{
              barmode: 'group',
              autosize: true,
              margin: { l: 50, r: 20, t: 20, b: 40 },
              paper_bgcolor: 'rgba(0,0,0,0)',
              plot_bgcolor: 'rgba(0,0,0,0)',
              yaxis: { title: { text: 'INR' } },
              legend: { orientation: 'h', y: -0.2 }
            }}
            useResizeHandler={true}
            style={{ width: '100%', height: '300px' }}
          />
        </div>

        {/* Chart 2: Goal Gap Comparison */}
        <div className="card p-4">
          <h2 className="text-lg font-bold mb-4 ml-4">Goal Gap (Shortfall / Surplus)</h2>
          <Plot
            data={[
              {
                x: ['Conservative', 'Expected', 'Optimistic'],
                y: [c.kpis.goal_gap_inr, e.kpis.goal_gap_inr, o.kpis.goal_gap_inr],
                type: 'bar',
                marker: {
                  color: [getBarColor(c.kpis.goal_gap_inr), getBarColor(e.kpis.goal_gap_inr), getBarColor(o.kpis.goal_gap_inr)]
                }
              }
            ]}
            layout={{
              autosize: true,
              margin: { l: 50, r: 20, t: 20, b: 40 },
              paper_bgcolor: 'rgba(0,0,0,0)',
              plot_bgcolor: 'rgba(0,0,0,0)',
              yaxis: { title: { text: 'INR (Positive = Shortfall)' } },
            }}
            useResizeHandler={true}
            style={{ width: '100%', height: '300px' }}
          />
        </div>

      </div>

      {/* Tabular Comparison */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-gray-700">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="p-4 font-semibold text-gray-900">Metric</th>
                <th className="p-4 font-semibold text-gray-900 border-l border-gray-100">Conservative</th>
                <th className="p-4 font-bold text-brand-700 border-l border-brand-100 bg-brand-50">Expected</th>
                <th className="p-4 font-semibold text-gray-900 border-l border-gray-100">Optimistic</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              <tr>
                <td className="p-4 font-medium">Future Property Value</td>
                <td className="p-4 border-l border-gray-100">{formatCurrency(c.property.future_value_inr)}</td>
                <td className="p-4 border-l border-brand-100 bg-brand-50/50 font-medium">{formatCurrency(e.property.future_value_inr)}</td>
                <td className="p-4 border-l border-gray-100">{formatCurrency(o.property.future_value_inr)}</td>
              </tr>
              <tr>
                <td className="p-4 font-medium">Real Wealth</td>
                <td className="p-4 border-l border-gray-100">{formatCurrency(c.wealth.real_wealth_inr)}</td>
                <td className="p-4 border-l border-brand-100 bg-brand-50/50 font-medium">{formatCurrency(e.wealth.real_wealth_inr)}</td>
                <td className="p-4 border-l border-gray-100">{formatCurrency(o.wealth.real_wealth_inr)}</td>
              </tr>
              <tr>
                <td className="p-4 font-medium">Goal Gap</td>
                <td className="p-4 border-l border-gray-100">{formatCurrency(c.kpis.goal_gap_inr)}</td>
                <td className="p-4 border-l border-brand-100 bg-brand-50/50 font-medium">{formatCurrency(e.kpis.goal_gap_inr)}</td>
                <td className="p-4 border-l border-gray-100">{formatCurrency(o.kpis.goal_gap_inr)}</td>
              </tr>
              <tr>
                <td className="p-4 font-medium">Affordability Ratio</td>
                <td className="p-4 border-l border-gray-100">{c.kpis.affordability_ratio.toFixed(2)}</td>
                <td className="p-4 border-l border-brand-100 bg-brand-50/50 font-medium">{e.kpis.affordability_ratio.toFixed(2)}</td>
                <td className="p-4 border-l border-gray-100">{o.kpis.affordability_ratio.toFixed(2)}</td>
              </tr>
              <tr>
                <td className="p-4 font-medium">Stress Category</td>
                <td className="p-4 border-l border-gray-100">
                   <span className={`px-2 py-1 rounded text-xs font-bold ${c.stress.category === 'Safe' ? 'bg-green-100 text-green-700' : c.stress.category === 'Risky' ? 'bg-red-100 text-red-700' : 'bg-yellow-100 text-yellow-700'}`}>
                     {c.stress.category}
                   </span>
                </td>
                <td className="p-4 border-l border-brand-100 bg-brand-50/50">
                  <span className={`px-2 py-1 rounded text-xs font-bold ${e.stress.category === 'Safe' ? 'bg-green-100 text-green-700' : e.stress.category === 'Risky' ? 'bg-red-100 text-red-700' : 'bg-brand-100 text-brand-700'}`}>
                     {e.stress.category}
                   </span>
                </td>
                <td className="p-4 border-l border-gray-100">
                  <span className={`px-2 py-1 rounded text-xs font-bold ${o.stress.category === 'Safe' ? 'bg-green-100 text-green-700' : o.stress.category === 'Risky' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
                     {o.stress.category}
                   </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
