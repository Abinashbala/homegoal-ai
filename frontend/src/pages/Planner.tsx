import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { usePlanner } from '../context/PlannerContext';
import { PlannerAPI } from '../api/client';
import { ChevronRight, Loader2 } from 'lucide-react';
import clsx from 'clsx';

export default function Planner() {
  const { requestParams, setRequestParams, setForecastResult, isLoading, setIsLoading } = usePlanner();
  const [step, setStep] = useState(1);
  const navigate = useNavigate();

  const handleInputChange = (section: keyof typeof requestParams, field: string, value: any) => {
    setRequestParams(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value === '' ? 0 : Number(value)
      }
    }));
  };

  const handleStringChange = (section: keyof typeof requestParams, field: string, value: string) => {
    setRequestParams(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value
      }
    }));
  };

  const handleSubmit = async () => {
    try {
      setIsLoading(true);
      const result = await PlannerAPI.getForecast(requestParams);
      setForecastResult(result);
      navigate('/results');
    } catch (error) {
      console.error('Error generating forecast:', error);
      alert('Failed to generate forecast. Please check backend connection.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 w-full pb-24">
      {/* Stepper Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Affordability Planner</h1>
        <div className="flex items-center gap-2 mt-4 text-sm font-medium">
          <span className={clsx("px-3 py-1 rounded-full", step >= 1 ? "bg-brand-100 text-brand-700" : "text-gray-400")}>1. Financials</span>
          <ChevronRight size={16} className="text-gray-300" />
          <span className={clsx("px-3 py-1 rounded-full", step >= 2 ? "bg-brand-100 text-brand-700" : "text-gray-400")}>2. Property</span>
          <ChevronRight size={16} className="text-gray-300" />
          <span className={clsx("px-3 py-1 rounded-full", step >= 3 ? "bg-brand-100 text-brand-700" : "text-gray-400")}>3. Review</span>
        </div>
      </div>

      <div className="card p-6 md:p-8">
        {step === 1 && (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold border-b pb-2">Financial Profile</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Monthly Salary (AED)</label>
                <input 
                  type="number" 
                  className="input-field"
                  value={requestParams.income.monthly_salary_aed || ''}
                  onChange={(e) => handleInputChange('income', 'monthly_salary_aed', e.target.value)}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Monthly Expenses (AED)</label>
                <input 
                  type="number" 
                  className="input-field"
                  value={requestParams.income.monthly_expenses_aed || ''}
                  onChange={(e) => handleInputChange('income', 'monthly_expenses_aed', e.target.value)}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Available savings: AED {(requestParams.income.monthly_salary_aed - requestParams.income.monthly_expenses_aed).toLocaleString()} / month
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Current Liquid Savings (AED)</label>
                <input 
                  type="number" 
                  className="input-field"
                  value={requestParams.savings.current_savings_aed || ''}
                  onChange={(e) => handleInputChange('savings', 'current_savings_aed', e.target.value)}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Current Investments (AED)</label>
                <input 
                  type="number" 
                  className="input-field"
                  value={requestParams.savings.current_investment_aed || ''}
                  onChange={(e) => handleInputChange('savings', 'current_investment_aed', e.target.value)}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Monthly Investment Contribution (AED)</label>
              <input 
                type="number" 
                className="input-field"
                value={requestParams.savings.monthly_investment_contrib_aed || ''}
                onChange={(e) => handleInputChange('savings', 'monthly_investment_contrib_aed', e.target.value)}
              />
              <p className="text-xs text-gray-500 mt-1">Amount from your available savings that will be invested (remainder stays in liquid savings).</p>
            </div>
            
            <div className="pt-4 flex justify-end">
              <button className="btn-primary" onClick={() => setStep(2)}>Next Step</button>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold border-b pb-2">Property Target</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Target City</label>
                <input 
                  type="text" 
                  className="input-field"
                  value={requestParams.property.city || ''}
                  onChange={(e) => handleStringChange('property', 'city', e.target.value)}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Locality</label>
                <input 
                  type="text" 
                  className="input-field"
                  value={requestParams.property.locality || ''}
                  onChange={(e) => handleStringChange('property', 'locality', e.target.value)}
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Property Size (SqFt)</label>
                <input 
                  type="number" 
                  className="input-field"
                  value={requestParams.property.sqft || ''}
                  onChange={(e) => handleInputChange('property', 'sqft', e.target.value)}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Current Price Per SqFt (INR)</label>
                <input 
                  type="number" 
                  className="input-field"
                  value={requestParams.property.current_price_per_sqft_inr || ''}
                  onChange={(e) => handleInputChange('property', 'current_price_per_sqft_inr', e.target.value)}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Target Purchase Year</label>
              <select 
                className="input-field"
                value={requestParams.property.target_year}
                onChange={(e) => handleInputChange('property', 'target_year', e.target.value)}
              >
                {Array.from({ length: 15 }).map((_, i) => {
                  const year = new Date().getFullYear() + 1 + i;
                  return <option key={year} value={year}>{year}</option>;
                })}
              </select>
            </div>
            
            <div className="pt-4 flex justify-between">
              <button className="btn-secondary" onClick={() => setStep(1)}>Back</button>
              <button className="btn-primary" onClick={() => setStep(3)}>Review</button>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold border-b pb-2">Review Summary</h2>
            
            <div className="bg-gray-50 p-4 rounded-lg space-y-3 text-sm">
              <div className="flex justify-between border-b border-gray-200 pb-2">
                <span className="text-gray-600">Property Location:</span>
                <span className="font-medium">{requestParams.property.locality}, {requestParams.property.city}</span>
              </div>
              <div className="flex justify-between border-b border-gray-200 pb-2">
                <span className="text-gray-600">Current Est. Value:</span>
                <span className="font-medium">₹{((requestParams.property.sqft * requestParams.property.current_price_per_sqft_inr)/100000).toFixed(2)} Lakhs</span>
              </div>
              <div className="flex justify-between border-b border-gray-200 pb-2">
                <span className="text-gray-600">Target Year:</span>
                <span className="font-medium">{requestParams.property.target_year} ({requestParams.property.target_year - new Date().getFullYear()} years)</span>
              </div>
              <div className="flex justify-between border-b border-gray-200 pb-2">
                <span className="text-gray-600">Current Total Wealth:</span>
                <span className="font-medium">AED {(requestParams.savings.current_savings_aed + requestParams.savings.current_investment_aed).toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Monthly Savings Capacity:</span>
                <span className="font-medium text-success-500">AED {(requestParams.income.monthly_salary_aed - requestParams.income.monthly_expenses_aed).toLocaleString()}</span>
              </div>
            </div>
            
            <div className="pt-4 flex justify-between">
              <button className="btn-secondary" onClick={() => setStep(2)}>Back</button>
              <button 
                className="btn-primary flex items-center gap-2" 
                onClick={handleSubmit}
                disabled={isLoading}
              >
                {isLoading ? <Loader2 className="animate-spin" size={18} /> : null}
                Generate Forecast
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
