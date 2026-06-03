import axios from 'axios';
import { ForecastRequest, ForecastResponse, ModelComparisonResponse } from '../types';

const api = axios.create({
  baseURL: '/api', // Proxy set up in vite.config.ts routes to backend
  headers: {
    'Content-Type': 'application/json',
  },
});

export const PlannerAPI = {
  async getForecast(data: ForecastRequest): Promise<ForecastResponse> {
    const response = await api.post<ForecastResponse>('/forecast', data);
    return response.data;
  },
  
  async getModelComparison(): Promise<ModelComparisonResponse> {
    const response = await api.get<ModelComparisonResponse>('/model-comparison');
    return response.data;
  }
};
