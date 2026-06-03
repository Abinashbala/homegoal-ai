import { ReactNode } from 'react';
import clsx from 'clsx';

interface KPICardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: ReactNode;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  className?: string;
  color?: 'brand' | 'success' | 'danger' | 'warning' | 'default';
}

export default function KPICard({ 
  title, 
  value, 
  subtitle, 
  icon, 
  trend, 
  trendValue,
  className,
  color = 'default'
}: KPICardProps) {
  
  const colorMap = {
    brand: 'text-brand-700 bg-brand-50 border-brand-100',
    success: 'text-success-500 bg-green-50 border-green-100',
    danger: 'text-danger-500 bg-red-50 border-red-100',
    warning: 'text-warning-500 bg-yellow-50 border-yellow-100',
    default: 'text-gray-900 bg-white border-gray-100'
  };

  return (
    <div className={clsx("card p-5 flex flex-col justify-between", colorMap[color], className)}>
      <div className="flex justify-between items-start mb-2">
        <h3 className="text-sm font-medium text-gray-500">{title}</h3>
        {icon && <div className="text-gray-400">{icon}</div>}
      </div>
      
      <div>
        <div className="text-2xl font-bold mb-1 tracking-tight">{value}</div>
        
        {(subtitle || trendValue) && (
          <div className="flex items-center text-sm mt-2">
            {trendValue && (
              <span className={clsx(
                "mr-2 font-medium flex items-center",
                trend === 'up' && 'text-success-500',
                trend === 'down' && 'text-danger-500',
                trend === 'neutral' && 'text-gray-500'
              )}>
                {trend === 'up' && '↑ '}
                {trend === 'down' && '↓ '}
                {trendValue}
              </span>
            )}
            {subtitle && <span className="text-gray-500">{subtitle}</span>}
          </div>
        )}
      </div>
    </div>
  );
}
