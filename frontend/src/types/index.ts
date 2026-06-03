// Match backend Pydantic models

export interface PropertyInput {
  sqft: number;
  current_price_per_sqft_inr: number;
  target_year: number;
  city?: string;
  locality?: string;
}

export interface IncomeInput {
  monthly_salary_aed: number;
  monthly_expenses_aed: number;
}

export interface SavingsInput {
  current_savings_aed: number;
  current_investment_aed: number;
  monthly_investment_contrib_aed: number;
  savings_return_pct?: number;
  investment_return_pct?: number;
}

export interface UserPreferences {
  risk_tolerance: 'conservative' | 'moderate' | 'aggressive';
  include_rental_savings: boolean;
}

export interface ForecastRequest {
  property: PropertyInput;
  income: IncomeInput;
  savings: SavingsInput;
  preferences: UserPreferences;
}

// ── Responses ──

export interface PropertyValues {
  current_value_inr: number;
  future_value_inr: number;
  appreciation_pct: number;
  hpi_cagr_used_pct: number;
}

export interface WealthValues {
  future_wealth_aed: number;
  fx_rate_at_target: number;
  future_wealth_inr_nominal: number;
  real_wealth_inr: number;
  cumulative_inflation_mult: number;
  monthly_savings_aed: number;
  monthly_savings_rate_pct: number;
}

export interface AffordabilityKPIs {
  affordability_ratio: number;
  affordability_label: string;
  goal_gap_inr: number;
  goal_gap_label: string;
  required_extra_savings_inr: number;
  required_extra_savings_aed: number;
  wealth_coverage_pct: number;
  fx_tailwind_pct: number;
  years_remaining: number;
}

export interface StressBreakdown {
  goal_gap_ratio: number;
  expense_ratio: number;
  coverage_shortfall: number;
  risk_multiplier: number;
  weighted_raw_score: number;
}

export interface StressScoreResult {
  score: number;
  category: 'Safe' | 'Comfortable' | 'Stretch' | 'Risky' | string;
  primary_driver: string;
  explanation: string;
  recommendation: string;
  breakdown: StressBreakdown;
}

export interface SingleScenarioResult {
  scenario: string;
  property: PropertyValues;
  wealth: WealthValues;
  kpis: AffordabilityKPIs;
  stress: StressScoreResult;
}

export interface ForecastResponse {
  request_id: string;
  computed_at: string;
  years_horizon: number;
  target_year: number;
  current_year: number;
  city?: string;
  locality?: string;
  conservative: SingleScenarioResult;
  expected: SingleScenarioResult;
  optimistic: SingleScenarioResult;
  summary: {
    recommended_scenario: string;
    expected_affordability_ratio: number;
    is_achievable_in_expected: boolean;
    years_to_target: number;
    key_takeaway: string;
  };
}

export interface ModelComparisonResponse {
  hpi: any;
  fx: any;
  scenario_parameters: any;
  selection_rationale: string;
}
