import { useState, useMemo } from 'react';
import { usePlanner } from '../context/PlannerContext';
import { Navigate, Link } from 'react-router-dom';
import KPICard from '../components/KPICard';
import StressMeter from '../components/StressMeter';
import { formatCurrency, formatPercent } from '../utils/format';
import { PlannerAPI } from '../api/client';
import { Loader2, X, Home, Clock, GraduationCap } from 'lucide-react';

// ── EMI Calculator helper ─────────────────────────────────────────────────────
function calcEMI(principal: number, annualRatePct: number, tenureYears: number) {
  if (principal <= 0 || annualRatePct <= 0 || tenureYears <= 0) {
    return { emi: 0, totalInterest: 0, totalRepayment: 0, loanAmount: principal };
  }
  const monthlyRate = annualRatePct / 100 / 12;
  const n = tenureYears * 12;
  const emi = (principal * monthlyRate * Math.pow(1 + monthlyRate, n)) / (Math.pow(1 + monthlyRate, n) - 1);
  const totalRepayment = emi * n;
  const totalInterest = totalRepayment - principal;
  return { emi, totalInterest, totalRepayment, loanAmount: principal };
}

// ── Comparison Modal ──────────────────────────────────────────────────────────
interface ComparisonModalProps {
  onClose: () => void;
  buyNow: {
    propertyValueInr: number;
    loanAmount: number;
    downPayment: number;
    emi: number;
    totalInterest: number;
    totalRepayment: number;
    purchaseYear: number;
    interestRate: number;
    loanTenure: number;
  };
  wait: {
    futurePropertyValueInr: number;
    currentPropertyValueInr: number;
    realWealthInr: number;
    goalGapInr: number;
    targetYear: number;
    currentYear: number;
  };
}

function ComparisonModal({ onClose, buyNow, wait }: ComparisonModalProps) {
  const currentYear = new Date().getFullYear();
  const waitYears = wait.targetYear - currentYear;

  // Derived display metrics — pure arithmetic, no business logic change
  const appreciationInr = wait.futurePropertyValueInr - wait.currentPropertyValueInr;
  const appreciationPct = wait.currentPropertyValueInr > 0
    ? (appreciationInr / wait.currentPropertyValueInr) * 100
    : 0;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      aria-label="Buy Now vs Wait Comparison"
    >
      {/* Backdrop */}
      <div className="absolute inset-0 bg-gray-900/60 backdrop-blur-sm" onClick={onClose} />

      {/* Modal panel */}
      <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-3xl max-h-[90vh] overflow-y-auto">

        {/* Header */}
        <div className="flex justify-between items-start p-6 border-b border-gray-100 sticky top-0 bg-white z-10 rounded-t-2xl">
          <div>
            <h2 className="text-xl font-bold text-gray-900">Buy Now vs Wait — Comparison</h2>
            <p className="text-sm text-gray-500 mt-0.5">Data only. No recommendation is made.</p>
          </div>
          <button onClick={onClose} className="p-2 rounded-lg hover:bg-gray-100 transition-colors" aria-label="Close">
            <X size={20} className="text-gray-500" />
          </button>
        </div>

        {/* Section 1: Snapshot */}
        <div className="px-6 pt-6">
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">Snapshot</h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="bg-gray-50 rounded-xl p-4 border border-gray-100">
              <p className="text-xs text-gray-500 mb-1">Current Property Value</p>
              <p className="text-base font-bold text-gray-900">{formatCurrency(wait.currentPropertyValueInr)}</p>
            </div>
            <div className="bg-gray-50 rounded-xl p-4 border border-gray-100">
              <p className="text-xs text-gray-500 mb-1">Future Property Value</p>
              <p className="text-base font-bold text-gray-900">{formatCurrency(wait.futurePropertyValueInr)}</p>
            </div>
            <div className="bg-amber-50 rounded-xl p-4 border border-amber-100">
              <p className="text-xs text-amber-600 mb-1">Increase (Cost of Waiting)</p>
              <p className="text-base font-bold text-amber-700">{formatCurrency(appreciationInr)}</p>
              <p className="text-xs text-amber-500 mt-0.5">+{appreciationPct.toFixed(1)}%</p>
            </div>
            <div className="bg-brand-50 rounded-xl p-4 border border-brand-100">
              <p className="text-xs text-brand-600 mb-1">Years Delayed</p>
              <p className="text-base font-bold text-brand-700">{waitYears} Years</p>
            </div>
          </div>
        </div>

        {/* Section 2: Ownership Timeline */}
        <div className="px-6 pt-6">
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">Ownership Timeline</h3>

          {/* Buy Now row */}
          <div className="mb-4">
            <div className="flex items-center gap-2 mb-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 flex-none" />
              <span className="text-xs font-semibold text-emerald-700 uppercase tracking-wide">Buy Now Path</span>
            </div>
            <div className="flex items-center gap-0 text-xs">
              <span className="flex-none bg-emerald-100 text-emerald-800 font-bold px-2 py-1 rounded-l-md border border-emerald-200">{currentYear}</span>
              <div className="flex-1 h-6 bg-emerald-50 border-t border-b border-emerald-200 flex items-center px-3">
                <Home size={12} className="text-emerald-600 mr-1.5" />
                <span className="text-emerald-700 font-medium">Ownership starts immediately</span>
              </div>
              <span className="flex-none bg-emerald-500 text-white font-bold px-2 py-1 rounded-r-md text-[10px]">Owned</span>
            </div>
          </div>

          {/* Wait row */}
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-500 flex-none" />
              <span className="text-xs font-semibold text-amber-700 uppercase tracking-wide">Wait Path</span>
            </div>
            <div className="flex items-center gap-0 text-xs">
              <span className="flex-none bg-amber-50 text-amber-800 font-bold px-2 py-1 rounded-l-md border border-amber-200">{currentYear}</span>
              <div className="flex-1 h-6 bg-amber-50 border-t border-b border-amber-200 flex items-center px-3">
                <Clock size={12} className="text-amber-500 mr-1.5" />
                <span className="text-amber-700 font-medium">Saving period — {waitYears} years</span>
              </div>
              <span className="flex-none bg-amber-500 text-white font-bold px-2 py-1 rounded-r-md text-[10px]">{wait.targetYear}</span>
            </div>
            <p className="text-xs text-gray-400 mt-1.5 ml-1">Purchase occurs in {wait.targetYear} using accumulated savings.</p>
          </div>
        </div>

        {/* Section 3: Financial Comparison Table */}
        <div className="px-6 pt-6">
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">Financial Comparison</h3>
          <div className="rounded-xl border border-gray-200 overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr>
                  <th className="p-4 text-left font-semibold text-gray-600 bg-gray-50 w-2/5">Metric</th>
                  <th className="p-4 text-right font-bold text-emerald-700 bg-emerald-50 w-[30%]">
                    <div className="flex items-center justify-end gap-1.5"><Home size={14} /> Buy Now</div>
                  </th>
                  <th className="p-4 text-right font-bold text-amber-700 bg-amber-50 w-[30%]">
                    <div className="flex items-center justify-end gap-1.5"><Clock size={14} /> Wait</div>
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                <tr>
                  <td className="p-4 text-gray-700 font-medium">Property Value</td>
                  <td className="p-4 text-right font-semibold text-gray-900">{formatCurrency(buyNow.propertyValueInr)}</td>
                  <td className="p-4 text-right font-semibold text-gray-900">{formatCurrency(wait.futurePropertyValueInr)}</td>
                </tr>
                <tr className="bg-gray-50/50">
                  <td className="p-4 text-gray-700 font-medium">Purchase Year</td>
                  <td className="p-4 text-right text-gray-900">{buyNow.purchaseYear}</td>
                  <td className="p-4 text-right text-gray-900">{wait.targetYear}</td>
                </tr>
                <tr>
                  <td className="p-4 text-gray-700 font-medium">Wealth Available</td>
                  <td className="p-4 text-right text-gray-900">
                    {formatCurrency(buyNow.downPayment)} <span className="text-xs text-gray-400">(down pmt)</span>
                  </td>
                  <td className="p-4 text-right text-gray-900">{formatCurrency(wait.realWealthInr)}</td>
                </tr>
                {/* Renamed "Goal Gap" → "Property Funding" with explicit wording per spec */}
                <tr className="bg-gray-50/50">
                  <td className="p-4 text-gray-700 font-medium">Property Funding</td>
                  <td className="p-4 text-right text-gray-900">
                    <span className="text-gray-500 text-xs">Loan Required: </span>
                    <span className="font-medium">{formatCurrency(buyNow.loanAmount)}</span>
                  </td>
                  <td className="p-4 text-right">
                    {wait.goalGapInr > 0 ? (
                      <span className="text-amber-600 font-medium">
                        Shortfall: {formatCurrency(wait.goalGapInr)}
                      </span>
                    ) : (
                      <span className="text-emerald-600 font-medium">
                        Surplus: {formatCurrency(Math.abs(wait.goalGapInr))}
                      </span>
                    )}
                  </td>
                </tr>
                <tr>
                  <td className="p-4 text-gray-700 font-medium">EMI</td>
                  <td className="p-4 text-right text-gray-900">
                    {buyNow.emi > 0 ? formatCurrency(buyNow.emi) : '—'} <span className="text-xs text-gray-400">/mo</span>
                  </td>
                  <td className="p-4 text-right text-gray-500">—</td>
                </tr>
                <tr className="bg-gray-50/50">
                  <td className="p-4 text-gray-700 font-medium">Total Interest</td>
                  <td className="p-4 text-right text-gray-900">{buyNow.totalInterest > 0 ? formatCurrency(buyNow.totalInterest) : '—'}</td>
                  <td className="p-4 text-right text-gray-500">—</td>
                </tr>
                <tr>
                  <td className="p-4 text-gray-700 font-medium">Total Repayment</td>
                  <td className="p-4 text-right font-semibold text-gray-900">{buyNow.totalRepayment > 0 ? formatCurrency(buyNow.totalRepayment) : '—'}</td>
                  <td className="p-4 text-right text-gray-500">—</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Section 4: Loan Assumptions */}
        <div className="px-6 pt-6">
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">Loan Assumptions</h3>
          <div className="bg-gray-50 rounded-xl border border-gray-100 divide-y divide-gray-100">
            {[
              { label: 'Loan Amount',     value: formatCurrency(buyNow.loanAmount) },
              { label: 'Interest Rate',   value: `${buyNow.interestRate.toFixed(1)}% per annum` },
              { label: 'Loan Tenure',     value: `${buyNow.loanTenure} Years` },
              { label: 'Monthly EMI',     value: buyNow.emi > 0 ? `${formatCurrency(buyNow.emi)} / month` : '—' },
              { label: 'Total Interest',  value: buyNow.totalInterest > 0 ? formatCurrency(buyNow.totalInterest) : '—' },
              { label: 'Total Repayment', value: buyNow.totalRepayment > 0 ? formatCurrency(buyNow.totalRepayment) : '—' },
            ].map(({ label, value }) => (
              <div key={label} className="flex justify-between items-center px-4 py-3 text-sm">
                <span className="text-gray-600">{label}</span>
                <span className="font-semibold text-gray-900">{value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Section 5: Cost Components */}
        <div className="px-6 pt-6">
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">Cost Components</h3>
          <p className="text-xs text-gray-500 mb-3">
            Two different cost types — presented for transparency. No comparison implied.
          </p>
          <div className="grid grid-cols-2 gap-3">
            <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4">
              <p className="text-xs font-semibold text-emerald-700 mb-1">Loan Interest Cost</p>
              <p className="text-lg font-bold text-emerald-800">
                {buyNow.totalInterest > 0 ? formatCurrency(buyNow.totalInterest) : '—'}
              </p>
              <p className="text-xs text-emerald-600 mt-1 leading-relaxed">
                Extra paid to the bank over {buyNow.loanTenure} years (Buy Now path).
              </p>
            </div>
            <div className="rounded-xl border border-amber-200 bg-amber-50 p-4">
              <p className="text-xs font-semibold text-amber-700 mb-1">Property Appreciation Cost</p>
              <p className="text-lg font-bold text-amber-800">
                {appreciationInr >= 0 ? formatCurrency(appreciationInr) : '—'}
              </p>
              <p className="text-xs text-amber-600 mt-1 leading-relaxed">
                Price increase of +{appreciationPct.toFixed(1)}% over {waitYears} years (Wait path).
              </p>
            </div>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="p-6 pt-5">
          <p className="text-xs text-gray-400 leading-relaxed">
            This comparison presents data only. It does not constitute financial advice or a recommendation to buy or wait.
            All figures are estimates based on the inputs provided. Consult a qualified financial advisor before making any
            property investment decision.
          </p>
        </div>

      </div>
    </div>
  );
}

// ── Main Results Page ─────────────────────────────────────────────────────────
export default function Results() {
  const { forecastResult, requestParams, setRequestParams, setForecastResult } = usePlanner();
  const [isRecalculating, setIsRecalculating] = useState(false);

  // ── Buy Now Calculator State ───────────────────────────────────────────────
  const [activePath, setActivePath] = useState<'saving' | 'buynow'>('saving');
  const [downPayment, setDownPayment] = useState(0);
  const [interestRate, setInterestRate] = useState(8.5);
  const [loanTenure, setLoanTenure] = useState(20);
  const [showModal, setShowModal] = useState(false);

  if (!forecastResult) {
    return <Navigate to="/planner" />;
  }

  const result = forecastResult.expected; // Main display defaults to Expected scenario — UNCHANGED
  const prop = result.property;
  const wealth = result.wealth;
  const kpi = result.kpis;
  const stress = result.stress;

  const gapText = kpi.goal_gap_inr > 0
    ? `To fully achieve this goal you may need to save an additional ${formatCurrency(kpi.required_extra_savings_inr)} per month.`
    : 'You are on track to achieve this goal with a surplus.';

  // ── What-If Handlers — UNCHANGED ──────────────────────────────────────────
  const handleWhatIf = async (field: string, value: number) => {
    setIsRecalculating(true);
    const newReq = JSON.parse(JSON.stringify(requestParams));
    if (field === 'target_year') newReq.property.target_year = value;
    else if (field === 'monthly_investment') newReq.savings.monthly_investment_contrib_aed = value;
    else if (field === 'investment_return') newReq.savings.investment_return_pct = value;
    setRequestParams(newReq);
    try {
      const res = await PlannerAPI.getForecast(newReq);
      setForecastResult(res);
    } catch (e) {
      console.error(e);
    } finally {
      setIsRecalculating(false);
    }
  };

  // ── Buy Now Calculations — UNCHANGED ──────────────────────────────────────
  const currentPropertyValueInr = prop.current_value_inr;
  const safeDownPayment = Math.min(downPayment, currentPropertyValueInr);
  const loanAmount = Math.max(0, currentPropertyValueInr - safeDownPayment);
  const { emi, totalInterest, totalRepayment } = useMemo(
    () => calcEMI(loanAmount, interestRate, loanTenure),
    [loanAmount, interestRate, loanTenure]
  );

  return (
    <>
      {/* Comparison Modal */}
      {showModal && (
        <ComparisonModal
          onClose={() => setShowModal(false)}
          buyNow={{
            propertyValueInr: currentPropertyValueInr,
            loanAmount,
            downPayment: safeDownPayment,
            emi,
            totalInterest,
            totalRepayment,
            purchaseYear: new Date().getFullYear(),
            interestRate,
            loanTenure,
          }}
          wait={{
            futurePropertyValueInr: prop.future_value_inr,
            currentPropertyValueInr: prop.current_value_inr,
            realWealthInr: wealth.real_wealth_inr,
            goalGapInr: kpi.goal_gap_inr,
            targetYear: forecastResult.target_year,
            currentYear: forecastResult.current_year,
          }}
        />
      )}

      <div className="max-w-7xl mx-auto px-4 py-8 w-full">
        <div className="flex justify-between items-end mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Affordability Results</h1>
            <p className="text-gray-500 mt-1">Based on {forecastResult.years_horizon}-year expected scenario projections.</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

          {/* Left Column: KPIs & Stress — UNCHANGED */}
          <div className="lg:col-span-2 space-y-6">

            {/* Explanation Panel */}
            <div className="card p-6 bg-brand-50 border-brand-100 text-brand-900">
              <h2 className="text-lg font-bold mb-3 flex items-center gap-2">
                <span className="text-2xl">💡</span> Your Personal Forecast
              </h2>
              <p className="leading-relaxed text-base">
                You are projected to accumulate <strong>{formatCurrency(wealth.real_wealth_inr)}</strong> (real purchasing power) by {forecastResult.target_year}.{' '}
                The target property in {forecastResult.locality || 'your area'} may cost approximately <strong>{formatCurrency(prop.future_value_inr)}</strong> by then, due to a projected {formatPercent(prop.appreciation_pct)} total appreciation.{' '}
                Your affordability ratio is <strong>{kpi.affordability_ratio.toFixed(2)}</strong>. {gapText}
              </p>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 relative">
              {isRecalculating && (
                <div className="absolute inset-0 bg-white/50 backdrop-blur-sm z-10 flex items-center justify-center rounded-xl">
                  <Loader2 className="animate-spin text-brand-600 w-8 h-8" />
                </div>
              )}
              <KPICard
                title="Future Property Cost"
                value={formatCurrency(prop.future_value_inr)}
                subtitle={`From ${formatCurrency(prop.current_value_inr)} today`}
              />
              <KPICard
                title="Future Real Wealth"
                value={formatCurrency(wealth.real_wealth_inr)}
                subtitle={`Nominal: ${formatCurrency(wealth.future_wealth_inr_nominal)}`}
                color="success"
              />
              <KPICard
                title="Goal Gap"
                value={formatCurrency(Math.abs(kpi.goal_gap_inr))}
                subtitle={kpi.goal_gap_inr > 0 ? 'Shortfall' : 'Surplus'}
                color={kpi.goal_gap_inr > 0 ? 'warning' : 'success'}
              />
              <KPICard
                title="Affordability Ratio"
                value={kpi.affordability_ratio.toFixed(2)}
                subtitle={`Target: >= 1.0`}
              />
              <KPICard
                title="Required Extra Savings"
                value={kpi.required_extra_savings_inr > 0 ? formatCurrency(kpi.required_extra_savings_inr) : 'None'}
                subtitle="Per month"
              />
              <KPICard
                title="Projected FX Rate"
                value={`₹${wealth.fx_rate_at_target.toFixed(2)}`}
                subtitle={`${formatPercent(kpi.fx_tailwind_pct)} tailwind`}
              />
            </div>

            <StressMeter
              score={stress.score}
              category={stress.category}
              explanation={stress.explanation}
            />
          </div>

          {/* Right Column: What-If Analysis & Buy-Now Calculator */}
          <div className="space-y-6">
            <div className="card p-6 sticky top-24">
              <h2 className="text-xl font-bold mb-5">What-If Analysis &amp; Buy-Now Calculator using loan</h2>

              {/* Toggle */}
              <div className="flex rounded-lg border border-gray-200 overflow-hidden mb-6">
                <button
                  onClick={() => setActivePath('saving')}
                  className={`flex-1 py-2 text-sm font-medium transition-colors ${
                    activePath === 'saving'
                      ? 'bg-brand-700 text-white'
                      : 'bg-white text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  Saving Path
                </button>
                <button
                  onClick={() => setActivePath('buynow')}
                  className={`flex-1 py-2 text-sm font-medium transition-colors ${
                    activePath === 'buynow'
                      ? 'bg-brand-700 text-white'
                      : 'bg-white text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  Buy Now Path
                </button>
              </div>

              {/* SAVING PATH — UNCHANGED */}
              {activePath === 'saving' && (
                <>
                  <div className="space-y-8">
                    <div>
                      <div className="flex justify-between mb-2">
                        <label className="text-sm font-medium text-gray-700">Target Year</label>
                        <span className="font-bold text-brand-700">{requestParams.property.target_year}</span>
                      </div>
                      <input
                        type="range"
                        min={new Date().getFullYear() + 1}
                        max={new Date().getFullYear() + 15}
                        value={requestParams.property.target_year}
                        onChange={(e) => handleWhatIf('target_year', parseInt(e.target.value))}
                        onMouseUp={(e) => handleWhatIf('target_year', parseInt(e.currentTarget.value))}
                        onTouchEnd={(e) => handleWhatIf('target_year', parseInt(e.currentTarget.value))}
                      />
                    </div>

                    <div>
                      <div className="flex justify-between mb-2">
                        <label className="text-sm font-medium text-gray-700">Monthly Investment (AED)</label>
                        <span className="font-bold text-brand-700">{requestParams.savings.monthly_investment_contrib_aed.toLocaleString()}</span>
                      </div>
                      <input
                        type="range"
                        min={0}
                        max={requestParams.income.monthly_salary_aed - requestParams.income.monthly_expenses_aed}
                        step={500}
                        value={requestParams.savings.monthly_investment_contrib_aed}
                        onChange={(e) => {
                          const newReq = { ...requestParams };
                          newReq.savings.monthly_investment_contrib_aed = parseInt(e.target.value);
                          setRequestParams(newReq);
                        }}
                        onMouseUp={(e) => handleWhatIf('monthly_investment', parseInt(e.currentTarget.value))}
                        onTouchEnd={(e) => handleWhatIf('monthly_investment', parseInt(e.currentTarget.value))}
                      />
                      <div className="flex justify-between text-xs text-gray-400 mt-1">
                        <span>0</span>
                        <span>Max: {(requestParams.income.monthly_salary_aed - requestParams.income.monthly_expenses_aed).toLocaleString()}</span>
                      </div>
                    </div>
                  </div>

                  <div className="mt-8 pt-6 border-t border-gray-100">
                    <h3 className="text-sm font-medium text-gray-500 mb-4">Live Stress Drivers</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center text-sm">
                        <span className="text-gray-600">Goal Gap Ratio</span>
                        <span className="font-medium">{(stress.breakdown.goal_gap_ratio * 100).toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-gray-100 rounded-full h-1.5">
                        <div className="bg-warning-500 h-1.5 rounded-full" style={{ width: `${stress.breakdown.goal_gap_ratio * 100}%` }} />
                      </div>

                      <div className="flex justify-between items-center text-sm mt-3">
                        <span className="text-gray-600">Coverage Shortfall</span>
                        <span className="font-medium">{(stress.breakdown.coverage_shortfall * 100).toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-gray-100 rounded-full h-1.5">
                        <div className="bg-danger-500 h-1.5 rounded-full" style={{ width: `${stress.breakdown.coverage_shortfall * 100}%` }} />
                      </div>
                    </div>
                  </div>
                </>
              )}

              {/* BUY NOW PATH — UNCHANGED */}
              {activePath === 'buynow' && (
                <div className="space-y-5">
                  {/* Auto-populated property price */}
                  <div className="bg-gray-50 rounded-lg p-3 border border-gray-100 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-500">Current Property Value</span>
                      <span className="font-semibold text-gray-900">{formatCurrency(currentPropertyValueInr)}</span>
                    </div>
                    <p className="text-xs text-gray-400 mt-1">Automatically sourced from your planner inputs.</p>
                  </div>

                  {/* Down Payment */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Down Payment (INR)</label>
                    <input
                      type="number"
                      className="input-field"
                      min={0}
                      max={currentPropertyValueInr}
                      step={50000}
                      value={downPayment || ''}
                      placeholder="e.g. 500000"
                      onChange={(e) => setDownPayment(parseFloat(e.target.value) || 0)}
                    />
                    <p className="text-xs text-gray-400 mt-1">
                      Loan Amount: <strong>{formatCurrency(loanAmount)}</strong>
                    </p>
                  </div>

                  {/* Interest Rate */}
                  <div>
                    <div className="flex justify-between mb-1">
                      <label className="text-sm font-medium text-gray-700">Interest Rate (%)</label>
                      <span className="font-bold text-brand-700">{interestRate.toFixed(1)}%</span>
                    </div>
                    <input
                      type="range"
                      min={4}
                      max={20}
                      step={0.5}
                      value={interestRate}
                      onChange={(e) => setInterestRate(parseFloat(e.target.value))}
                    />
                    <div className="flex justify-between text-xs text-gray-400 mt-1">
                      <span>4%</span><span>20%</span>
                    </div>
                  </div>

                  {/* Loan Tenure */}
                  <div>
                    <div className="flex justify-between mb-1">
                      <label className="text-sm font-medium text-gray-700">Loan Tenure (Years)</label>
                      <span className="font-bold text-brand-700">{loanTenure} yrs</span>
                    </div>
                    <input
                      type="range"
                      min={5}
                      max={30}
                      step={1}
                      value={loanTenure}
                      onChange={(e) => setLoanTenure(parseInt(e.target.value))}
                    />
                    <div className="flex justify-between text-xs text-gray-400 mt-1">
                      <span>5 yrs</span><span>30 yrs</span>
                    </div>
                  </div>

                  {/* Calculated outputs */}
                  <div className="border-t border-gray-100 pt-5 space-y-3 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Loan Amount</span>
                      <span className="font-semibold">{formatCurrency(loanAmount)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Monthly EMI</span>
                      <span className="font-semibold text-brand-700">{emi > 0 ? formatCurrency(emi) : '—'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Total Interest Paid</span>
                      <span className="font-semibold text-amber-600">{totalInterest > 0 ? formatCurrency(totalInterest) : '—'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Total Repayment</span>
                      <span className="font-semibold">{totalRepayment > 0 ? formatCurrency(totalRepayment) : '—'}</span>
                    </div>
                  </div>

                  <button
                    onClick={() => setShowModal(true)}
                    className="btn-primary w-full mt-2 text-center"
                    disabled={loanAmount <= 0 && downPayment <= 0}
                  >
                    View Full Comparison
                  </button>
                </div>
              )}

              {/* Wealth Growth Lab CTA */}
              <div className="mt-6 pt-6 border-t border-gray-100">
                <div className="bg-brand-50 border border-brand-100 rounded-xl p-5 text-center">
                  <h3 className="font-bold text-brand-900 mb-2 flex items-center justify-center gap-2">
                    <GraduationCap size={20} className="text-brand-600" />
                    How do I reach this goal?
                  </h3>
                  <p className="text-xs text-brand-800 mb-4 leading-relaxed">
                    Understand how time, inflation, and property appreciation affect your goal in the Wealth Growth Lab.
                  </p>
                  <Link to="/lab" className="btn-secondary w-full justify-center">
                    Explore Wealth Growth Lab
                  </Link>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </>
  );
}
