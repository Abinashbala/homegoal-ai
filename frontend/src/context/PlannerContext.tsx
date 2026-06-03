import React, { createContext, useContext, useState, ReactNode } from 'react';
import { ForecastRequest, ForecastResponse } from '../types';

interface PlannerContextProps {
  requestParams: ForecastRequest;
  setRequestParams: React.Dispatch<React.SetStateAction<ForecastRequest>>;
  forecastResult: ForecastResponse | null;
  setForecastResult: React.Dispatch<React.SetStateAction<ForecastResponse | null>>;
  isLoading: boolean;
  setIsLoading: React.Dispatch<React.SetStateAction<boolean>>;
}

const defaultRequest: ForecastRequest = {
  property: {
    sqft: 1200,
    current_price_per_sqft_inr: 8500,
    target_year: new Date().getFullYear() + 5,
    city: 'Chennai',
    locality: 'Porur',
  },
  income: {
    monthly_salary_aed: 20000,
    monthly_expenses_aed: 10000,
  },
  savings: {
    current_savings_aed: 50000,
    current_investment_aed: 20000,
    monthly_investment_contrib_aed: 2000,
  },
  preferences: {
    risk_tolerance: 'moderate',
    include_rental_savings: false,
  },
};

const PlannerContext = createContext<PlannerContextProps | undefined>(undefined);

export function PlannerProvider({ children }: { children: ReactNode }) {
  const [requestParams, setRequestParams] = useState<ForecastRequest>(defaultRequest);
  const [forecastResult, setForecastResult] = useState<ForecastResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  return (
    <PlannerContext.Provider value={{
      requestParams,
      setRequestParams,
      forecastResult,
      setForecastResult,
      isLoading,
      setIsLoading
    }}>
      {children}
    </PlannerContext.Provider>
  );
}

export function usePlanner() {
  const context = useContext(PlannerContext);
  if (!context) {
    throw new Error('usePlanner must be used within a PlannerProvider');
  }
  return context;
}
