import { useState } from 'react';
import { usePlanner } from '../context/PlannerContext';
import { Navigate } from 'react-router-dom';
import KPICard from '../components/KPICard';
import StressMeter from '../components/StressMeter';
import { formatCurrency, formatPercent } from '../utils/format';
import { PlannerAPI } from '../api/client';
import { Loader2 } from 'lucide-react';

export default function Results() {
  const { forecastResult, requestParams, setRequestParams, setForecastResult } = usePlanner();
  const [isRecalculating, setIsRecalculating] = useState(false);

  if (!forecastResult) {
    return <Navigate to="/planner" />;
  }

  const result = forecastResult.expected; // Main display defaults to Expected scenario
  const prop = result.property;
  const wealth = result.wealth;
  const kpi = result.kpis;
  const stress = result.stress;

  // Explanation Panel formatting
  const gapText = kpi.goal_gap_inr > 0 
    ? `To fully achieve this goal you may need to save an additional ${formatCurrency(kpi.required_extra_savings_inr)} per month.`
    : 'You are on track to achieve this goal with a surplus.';

  // What-If Handlers
  const handleWhatIf = async (field: string, value: number) => {
    setIsRecalculating(true);
    
    // Deep clone to avoid mutating state directly before set
    const newReq = JSON.parse(JSON.stringify(requestParams));
    
    if (field === 'target_year') {
      newReq.property.target_year = value;
    } else if (field === 'monthly_investment') {
      newReq.savings.monthly_investment_contrib_aed = value;
    } else if (field === 'investment_return') {
      newReq.savings.investment_return_pct = value;
    }

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

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 w-full">
      <div className="flex justify-between items-end mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Affordability Results</h1>
          <p className="text-gray-500 mt-1">Based on {forecastResult.years_horizon}-year expected scenario projections.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column: KPIs & Stress */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Explanation Panel */}
          <div className="card p-6 bg-brand-50 border-brand-100 text-brand-900">
            <h2 className="text-lg font-bold mb-3 flex items-center gap-2">
              <span className="text-2xl">💡</span> Your Personal Forecast
            </h2>
            <p className="leading-relaxed text-base">
              You are projected to accumulate <strong>{formatCurrency(wealth.real_wealth_inr)}</strong> (real purchasing power) by {forecastResult.target_year}. 
              The target property in {forecastResult.locality || 'your area'} may cost approximately <strong>{formatCurrency(prop.future_value_inr)}</strong> by then, due to a projected {formatPercent(prop.appreciation_pct)} total appreciation. 
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
              subtitle={kpi.goal_gap_inr > 0 ? "Shortfall" : "Surplus"}
              color={kpi.goal_gap_inr > 0 ? "warning" : "success"}
            />
            <KPICard 
              title="Affordability Ratio" 
              value={kpi.affordability_ratio.toFixed(2)} 
              subtitle={`Target: >= 1.0`}
            />
            <KPICard 
              title="Required Extra Savings" 
              value={kpi.required_extra_savings_inr > 0 ? formatCurrency(kpi.required_extra_savings_inr) : "None"} 
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

        {/* Right Column: What-If Analysis */}
        <div className="space-y-6">
          <div className="card p-6 sticky top-24">
            <h2 className="text-xl font-bold mb-6">What-If Analysis</h2>
            
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
                     // Using local state to update the slider quickly before API call could be better, but this works
                     // To prevent too many API calls, in a real app we'd debounce this.
                     const newReq = {...requestParams};
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
                   <div className="bg-warning-500 h-1.5 rounded-full" style={{ width: `${stress.breakdown.goal_gap_ratio * 100}%` }}></div>
                 </div>
                 
                 <div className="flex justify-between items-center text-sm mt-3">
                   <span className="text-gray-600">Coverage Shortfall</span>
                   <span className="font-medium">{(stress.breakdown.coverage_shortfall * 100).toFixed(1)}%</span>
                 </div>
                 <div className="w-full bg-gray-100 rounded-full h-1.5">
                   <div className="bg-danger-500 h-1.5 rounded-full" style={{ width: `${stress.breakdown.coverage_shortfall * 100}%` }}></div>
                 </div>
               </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
