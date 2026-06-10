import { useState } from 'react';
import { usePlanner } from '../context/PlannerContext';
import { Navigate } from 'react-router-dom';
import Plot from 'react-plotly.js';
import { formatCurrency, formatPercent } from '../utils/format';
import { BookOpen, AlertCircle, ShieldCheck, Banknote, LineChart, Target, TrendingUp, Home, GraduationCap } from 'lucide-react';

export default function WealthGrowthLab() {
  const { forecastResult, requestParams } = usePlanner();

  // Local state for the interactive compound growth simulator
  const [simSavings] = useState(requestParams.savings.current_savings_aed + requestParams.savings.current_investment_aed);
  const [simMonthly, setSimMonthly] = useState(requestParams.savings.monthly_investment_contrib_aed);
  const [simHorizon, setSimHorizon] = useState(forecastResult?.years_horizon || 10);
  const [simReturn, setSimReturn] = useState(8);

  if (!forecastResult) {
    return <Navigate to="/planner" />;
  }

  const result = forecastResult.expected;
  const prop = result.property;
  const wealth = result.wealth;
  const kpi = result.kpis;
  const req = requestParams;
  const currentYear = forecastResult.current_year;

  // Derive FX Rate accurately from KPIs
  const currentFx = kpi.fx_tailwind_pct !== 0 
    ? wealth.fx_rate_at_target / (1 + (kpi.fx_tailwind_pct / 100))
    : wealth.fx_rate_at_target;

  // ── 0. Why This Matters (Snapshot) ──
  const reqMonthlyStr = kpi.required_extra_savings_aed > 0
    ? formatCurrency(req.savings.monthly_investment_contrib_aed + kpi.required_extra_savings_aed).replace('₹', 'AED ')
    : formatCurrency(req.savings.monthly_investment_contrib_aed).replace('₹', 'AED ');

  // ── 1. Property vs Wealth Race ──
  const startWealthInr = (req.savings.current_savings_aed + req.savings.current_investment_aed) * currentFx;
  const endWealthInr = wealth.future_wealth_inr_nominal;
  const propStart = prop.current_value_inr;
  const propEnd = prop.future_value_inr;

  const wRate = Math.pow(endWealthInr / (startWealthInr || 1), 1 / forecastResult.years_horizon) - 1;
  const pRate = Math.pow(propEnd / propStart, 1 / forecastResult.years_horizon) - 1;

  const raceYears = [];
  const raceWealth = [];
  const raceProp = [];
  for (let i = 0; i <= forecastResult.years_horizon; i++) {
    raceYears.push(currentYear + i);
    raceWealth.push(startWealthInr * Math.pow(1 + wRate, i));
    raceProp.push(propStart * Math.pow(1 + pRate, i));
  }

  // ── 2. Compound Growth Simulator ──
  const simDataYears = [];
  const simDataPrincipal = [];
  const simDataGrowth = [];
  let totalPrincipal = simSavings;
  let totalGrowth = simSavings;
  const monthlyRate = simReturn / 100 / 12;

  for (let i = 0; i <= simHorizon; i++) {
    simDataYears.push(currentYear + i);
    simDataPrincipal.push(totalPrincipal);
    simDataGrowth.push(totalGrowth);
    if (i < simHorizon) {
      for (let m = 0; m < 12; m++) {
        totalGrowth = totalGrowth * (1 + monthlyRate) + simMonthly;
        totalPrincipal += simMonthly;
      }
    }
  }

  // ── 3. Time Is Your Biggest Asset ──
  const timeComparison = [5, 10, 15, 20].map(years => {
    let t = startWealthInr;
    for (let m = 0; m < years * 12; m++) {
      t = t * (1 + 0.08 / 12) + (req.savings.monthly_investment_contrib_aed * currentFx);
    }
    return { years, value: t };
  });

  // ── 5. Inflation Reality Check ──
  const annualInflationRate = Math.pow(wealth.cumulative_inflation_mult, 1 / forecastResult.years_horizon) - 1;
  const infYears = [0, 5, 10, 15];
  const infValues = infYears.map(y => propStart / Math.pow(1 + annualInflationRate, y));

  // ── 7. Currency Impact ──
  const sampleAed = wealth.future_wealth_aed;
  const currencyRates = [22, 24, currentFx, wealth.fx_rate_at_target].sort((a,b) => a-b);

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 w-full space-y-12">
      {/* Header */}
      <div className="border-b border-gray-200 pb-6">
        <h1 className="text-3xl font-bold text-gray-900 tracking-tight flex items-center gap-3">
          <BookOpen className="text-brand-600" size={32} />
          My Wealth Growth Lab
        </h1>
        <p className="text-gray-500 mt-2 max-w-3xl leading-relaxed">
          This educational module uses your actual planner inputs to explain the financial forces—like compounding, inflation, property appreciation, and currency—that influence your goal.
        </p>
      </div>

      {/* ── 0. Why This Matters Summary ── */}
      <section className="bg-brand-50 border border-brand-100 rounded-2xl p-6">
        <div className="flex flex-col lg:flex-row gap-8 items-center">
          <div className="flex-1">
            <h2 className="text-lg font-bold text-brand-900 mb-2">Why This Matters</h2>
            <p className="text-brand-800 text-sm leading-relaxed mb-4">
              This lab explains why the gap exists between what you save and what a property costs. 
              It shows how time, growth, inflation, and property appreciation directly impact your specific goal of buying in {forecastResult.locality || forecastResult.city}.
            </p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 w-full lg:w-auto flex-none">
            <div className="bg-white p-4 rounded-xl shadow-sm border border-brand-100">
              <p className="text-xs text-gray-500 mb-1">Target Property</p>
              <p className="font-bold text-gray-900">{formatCurrency(prop.future_value_inr)}</p>
            </div>
            <div className="bg-white p-4 rounded-xl shadow-sm border border-brand-100">
              <p className="text-xs text-gray-500 mb-1">Current Saving</p>
              <p className="font-bold text-gray-900">AED {req.savings.monthly_investment_contrib_aed.toLocaleString()}</p>
            </div>
            <div className="bg-white p-4 rounded-xl shadow-sm border border-brand-100">
              <p className="text-xs text-brand-600 mb-1">Required Saving</p>
              <p className="font-bold text-brand-700">{reqMonthlyStr}</p>
            </div>
            <div className="bg-white p-4 rounded-xl shadow-sm border border-brand-100">
              <p className="text-xs text-gray-500 mb-1">Time Remaining</p>
              <p className="font-bold text-gray-900">{forecastResult.years_horizon} Years</p>
            </div>
          </div>
        </div>
      </section>

      {/* ── 1. Property vs Wealth Race ── */}
      <section className="space-y-4">
        <div className="flex items-center gap-2">
          <Target className="text-indigo-600" size={24} />
          <h2 className="text-2xl font-bold text-gray-900">The Property vs Wealth Race</h2>
        </div>
        <p className="text-gray-500 text-sm max-w-3xl">
          Are you catching up or falling behind? This chart shows how fast your wealth is projected to grow (based on your planned contributions) compared to how fast your target property's price is expected to rise.
        </p>
        <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
          <div className="h-[400px]">
            <Plot
              data={[
                {
                  x: raceYears,
                  y: raceProp,
                  type: 'scatter',
                  mode: 'lines+markers',
                  name: 'Property Value',
                  line: { color: '#f59e0b', width: 3 },
                  marker: { size: 6 }
                },
                {
                  x: raceYears,
                  y: raceWealth,
                  type: 'scatter',
                  mode: 'lines+markers',
                  name: 'Your Wealth',
                  line: { color: '#10b981', width: 3 },
                  marker: { size: 6 }
                }
              ]}
              layout={{
                autosize: true,
                margin: { l: 60, r: 20, t: 30, b: 40 },
                legend: { orientation: 'h', y: -0.2 },
                paper_bgcolor: 'transparent',
                plot_bgcolor: 'transparent',
                yaxis: { title: { text: 'Value (INR)' }, gridcolor: '#f3f4f6' },
                xaxis: { gridcolor: '#f3f4f6' }
              }}
              useResizeHandler={true}
              style={{ width: '100%', height: '100%' }}
              config={{ displayModeBar: false }}
            />
          </div>
        </div>
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* ── 2. Compound Growth Simulator ── */}
        <section className="space-y-4">
          <div className="flex items-center gap-2">
            <TrendingUp className="text-emerald-600" size={24} />
            <h2 className="text-xl font-bold text-gray-900">Compound Growth Simulator</h2>
          </div>
          <p className="text-gray-500 text-sm">
            See how your AED {simMonthly.toLocaleString()}/mo savings contribution grows over time.
          </p>
          <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-sm space-y-5">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1">Monthly (AED)</label>
                <input 
                  type="number" className="w-full text-sm border-gray-300 rounded-lg p-2 bg-gray-50 border"
                  value={simMonthly} onChange={(e) => setSimMonthly(Number(e.target.value))}
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1">Growth Rate (%)</label>
                <input 
                  type="number" className="w-full text-sm border-gray-300 rounded-lg p-2 bg-gray-50 border"
                  value={simReturn} onChange={(e) => setSimReturn(Number(e.target.value))}
                />
              </div>
              <div className="col-span-2">
                <label className="block text-xs font-medium text-gray-500 mb-1">Years: {simHorizon}</label>
                <input 
                  type="range" min="1" max="30" className="w-full"
                  value={simHorizon} onChange={(e) => setSimHorizon(Number(e.target.value))}
                />
              </div>
            </div>
            <div className="h-[250px]">
              <Plot
                data={[
                  { x: simDataYears, y: simDataPrincipal, type: 'scatter', mode: 'none', fill: 'tozeroy', name: 'Contributions', fillcolor: '#cbd5e1' },
                  { x: simDataYears, y: simDataGrowth, type: 'scatter', mode: 'none', fill: 'tonexty', name: 'Growth', fillcolor: '#34d399' }
                ]}
                layout={{
                  autosize: true, margin: { l: 50, r: 10, t: 10, b: 30 },
                  legend: { orientation: 'h', y: -0.2 },
                  paper_bgcolor: 'transparent', plot_bgcolor: 'transparent',
                  yaxis: { gridcolor: '#f3f4f6' }, xaxis: { gridcolor: '#f3f4f6' }
                }}
                useResizeHandler={true} style={{ width: '100%', height: '100%' }} config={{ displayModeBar: false }}
              />
            </div>
          </div>
        </section>

        {/* ── 3. Time Is Your Biggest Asset ── */}
        <section className="space-y-4">
          <div className="flex items-center gap-2">
            <LineChart className="text-blue-600" size={24} />
            <h2 className="text-xl font-bold text-gray-900">Time Is Your Biggest Asset</h2>
          </div>
          <p className="text-gray-500 text-sm">
            Using your exact planned contribution of AED {req.savings.monthly_investment_contrib_aed.toLocaleString()}/month, see how much ending wealth is generated just by having more time.
          </p>
          <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-100">
                <tr>
                  <th className="py-3 px-4 text-left font-semibold text-gray-600">Years Invested</th>
                  <th className="py-3 px-4 text-right font-semibold text-gray-600">Ending Wealth (INR)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {timeComparison.map(row => (
                  <tr key={row.years} className={row.years === forecastResult.years_horizon ? 'bg-blue-50/50' : ''}>
                    <td className="py-4 px-4 font-medium text-gray-900 flex items-center gap-2">
                      {row.years} Years {row.years === forecastResult.years_horizon && <span className="bg-blue-100 text-blue-700 text-[10px] px-2 py-0.5 rounded-full font-bold">YOUR GOAL</span>}
                    </td>
                    <td className="py-4 px-4 text-right font-bold text-blue-700">{formatCurrency(row.value)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* ── 4. Property Price Growth ── */}
        <section className="space-y-4">
          <div className="flex items-center gap-2">
            <Home className="text-amber-600" size={24} />
            <h2 className="text-xl font-bold text-gray-900">The Cost of Waiting</h2>
          </div>
          <p className="text-gray-500 text-sm">
            Your target property is projected to appreciate at {formatPercent(prop.hpi_cagr_used_pct)} per year.
          </p>
          <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm flex flex-col justify-center h-[240px]">
            <div className="flex justify-between items-end mb-4">
              <div>
                <p className="text-xs text-gray-500 mb-1">Current Value ({currentYear})</p>
                <p className="text-xl font-bold text-gray-900">{formatCurrency(propStart)}</p>
              </div>
              <div className="text-right">
                <p className="text-xs text-gray-500 mb-1">Future Value ({forecastResult.target_year})</p>
                <p className="text-xl font-bold text-amber-600">{formatCurrency(propEnd)}</p>
              </div>
            </div>
            <div className="relative h-12 bg-gray-100 rounded-full overflow-hidden flex items-center">
              <div className="absolute left-0 h-full bg-gray-300" style={{ width: `${(propStart/propEnd)*100}%` }}></div>
              <div className="absolute right-0 h-full bg-amber-400" style={{ width: `${100 - (propStart/propEnd)*100}%` }}></div>
              <span className="absolute left-4 text-xs font-bold text-gray-700">Today's Price</span>
              <span className="absolute right-4 text-xs font-bold text-amber-900">Appreciation (+{formatCurrency(propEnd - propStart)})</span>
            </div>
          </div>
        </section>

        {/* ── 5. Inflation Reality Check ── */}
        <section className="space-y-4">
          <div className="flex items-center gap-2">
            <ShieldCheck className="text-rose-600" size={24} />
            <h2 className="text-xl font-bold text-gray-900">Inflation Reality Check</h2>
          </div>
          <p className="text-gray-500 text-sm">
            Inflation silently erodes purchasing power. Here is what {formatCurrency(propStart)} of today's money will actually buy in the future.
          </p>
          <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm h-[240px]">
             <div className="h-[180px]">
              <Plot
                data={[{
                  x: infYears.map(y => `Year ${y}`),
                  y: infValues,
                  type: 'bar',
                  marker: { color: ['#94a3b8', '#f43f5e', '#e11d48', '#be123c'] }
                }]}
                layout={{
                  autosize: true, margin: { l: 60, r: 10, t: 10, b: 30 },
                  paper_bgcolor: 'transparent', plot_bgcolor: 'transparent',
                  yaxis: { gridcolor: '#f3f4f6' }, xaxis: { gridcolor: 'transparent' }
                }}
                useResizeHandler={true} style={{ width: '100%', height: '100%' }} config={{ displayModeBar: false }}
              />
            </div>
          </div>
        </section>

        {/* ── 6. Goal Feasibility Check ── */}
        <section className="space-y-4">
          <div className="flex items-center gap-2">
            <AlertCircle className="text-orange-500" size={24} />
            <h2 className="text-xl font-bold text-gray-900">Goal Feasibility Check</h2>
          </div>
          <p className="text-gray-500 text-sm">
            Based on your actual planner results, here is your current position versus what is mathematically required.
          </p>
          <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
            <div className="p-5 border-b border-gray-100 flex justify-between items-center">
              <div>
                <p className="text-xs text-gray-500 mb-1">Required to reach {formatCurrency(propEnd)}</p>
                <p className="text-lg font-bold text-gray-900">{reqMonthlyStr}</p>
              </div>
            </div>
            <div className="p-5 border-b border-gray-100 flex justify-between items-center bg-gray-50">
              <div>
                <p className="text-xs text-gray-500 mb-1">Your Planned Contribution</p>
                <p className="text-lg font-bold text-gray-900">AED {req.savings.monthly_investment_contrib_aed.toLocaleString()}</p>
              </div>
            </div>
            <div className={`p-5 flex justify-between items-center ${kpi.goal_gap_inr > 0 ? 'bg-orange-50' : 'bg-emerald-50'}`}>
              <div>
                <p className={`text-xs mb-1 font-semibold ${kpi.goal_gap_inr > 0 ? 'text-orange-700' : 'text-emerald-700'}`}>Monthly Gap</p>
                <p className={`text-lg font-bold ${kpi.goal_gap_inr > 0 ? 'text-orange-800' : 'text-emerald-800'}`}>
                  {kpi.required_extra_savings_aed > 0 ? `Shortfall: AED ${kpi.required_extra_savings_aed.toLocaleString()}` : 'Surplus — On Track!'}
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* ── 7. Currency Impact Explorer ── */}
        <section className="space-y-4">
          <div className="flex items-center gap-2">
            <Banknote className="text-teal-600" size={24} />
            <h2 className="text-xl font-bold text-gray-900">Currency Impact Explorer</h2>
          </div>
          <p className="text-gray-500 text-sm">
            Your projected wealth is AED {sampleAed.toLocaleString()}. Here is what happens to your purchasing power in India if exchange rates change.
          </p>
          <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-sm">
            <div className="space-y-3">
              {currencyRates.map((rate, idx) => (
                <div key={idx} className="flex justify-between items-center border-b border-gray-100 pb-2 last:border-0 last:pb-0">
                  <div className="flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full ${rate === currentFx ? 'bg-teal-500' : 'bg-gray-300'}`} />
                    <span className="text-sm text-gray-600">If rate is 1 AED = {rate.toFixed(2)} INR</span>
                    {rate === currentFx && <span className="bg-teal-50 text-teal-700 text-[10px] px-2 py-0.5 rounded-full font-bold">Current</span>}
                    {rate === wealth.fx_rate_at_target && rate !== currentFx && <span className="bg-blue-50 text-blue-700 text-[10px] px-2 py-0.5 rounded-full font-bold">Projected Target</span>}
                  </div>
                  <span className="font-bold text-gray-900">{formatCurrency(sampleAed * rate)}</span>
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>

      {/* ── 8. Educational Micro Lessons ── */}
      <section className="border-t border-gray-200 pt-10">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
          <GraduationCap className="text-brand-600" size={28} />
          Educational Micro-Lessons
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white p-5 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
            <TrendingUp size={20} className="text-emerald-500 mb-3" />
            <h3 className="font-bold text-gray-900 mb-2">Why Saving Alone Fails</h3>
            <p className="text-sm text-gray-500 leading-relaxed">Property prices often rise faster than you can save money from a salary. Investing helps your money keep pace with asset inflation.</p>
          </div>
          <div className="bg-white p-5 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
            <Target size={20} className="text-blue-500 mb-3" />
            <h3 className="font-bold text-gray-900 mb-2">The Magic of Compounding</h3>
            <p className="text-sm text-gray-500 leading-relaxed">Returns generate their own returns. The earlier you start, the less you have to contribute out of pocket to reach the same goal.</p>
          </div>
          <div className="bg-white p-5 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
            <ShieldCheck size={20} className="text-rose-500 mb-3" />
            <h3 className="font-bold text-gray-900 mb-2">Inflation is a Tax</h3>
            <p className="text-sm text-gray-500 leading-relaxed">Cash loses value every year. If inflation is 5%, your uninvested savings buy 5% less house next year. Growth must beat inflation.</p>
          </div>
          <div className="bg-white p-5 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
            <Banknote size={20} className="text-teal-500 mb-3" />
            <h3 className="font-bold text-gray-900 mb-2">Currency Risk</h3>
            <p className="text-sm text-gray-500 leading-relaxed">As an NRI earning AED, a strengthening INR makes Indian property more expensive for you, even if the property price itself doesn't change.</p>
          </div>
        </div>
      </section>

      {/* Disclaimer */}
      <div className="bg-gray-50 p-6 rounded-2xl border border-gray-200 mt-12">
        <p className="text-xs text-gray-500 text-center leading-relaxed max-w-4xl mx-auto">
          <strong>Important Notice:</strong> The Wealth Growth Lab is an educational tool designed to help you understand financial concepts such as compounding, inflation, and currency impact. It uses estimates and assumptions from your planner context for illustrative purposes only. This module does not provide investment advice, recommend specific products, or guarantee future returns. Please consult a licensed financial advisor before making any investment decisions.
        </p>
      </div>

    </div>
  );
}
