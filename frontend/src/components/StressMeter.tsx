import clsx from 'clsx';
import { ShieldCheck, AlertCircle, AlertTriangle, XCircle } from 'lucide-react';

interface StressMeterProps {
  score: number;
  category: string;
  explanation: string;
}

export default function StressMeter({ score, category, explanation }: StressMeterProps) {
  // Determine colors based on category
  let colorClass = 'bg-gray-200';
  let textClass = 'text-gray-700';
  let Icon = ShieldCheck;
  
  if (category === 'Safe') {
    colorClass = 'bg-success-500';
    textClass = 'text-success-500';
    Icon = ShieldCheck;
  } else if (category === 'Comfortable') {
    colorClass = 'bg-brand-500';
    textClass = 'text-brand-500';
    Icon = AlertCircle;
  } else if (category === 'Stretch') {
    colorClass = 'bg-warning-500';
    textClass = 'text-warning-500';
    Icon = AlertTriangle;
  } else if (category === 'Risky') {
    colorClass = 'bg-danger-500';
    textClass = 'text-danger-500';
    Icon = XCircle;
  }

  // Cap score between 0 and 100 for width
  const safeScore = Math.min(100, Math.max(0, score));

  return (
    <div className="card p-6 border-t-4" style={{ borderTopColor: `var(--color-${category.toLowerCase()})` }}>
      <div className="flex items-center gap-3 mb-4">
        <div className={clsx("p-2 rounded-full bg-opacity-10", textClass, colorClass.replace('bg-', 'bg-').replace('500', '100'))}>
          <Icon size={24} className={textClass} />
        </div>
        <div>
          <h2 className="text-lg font-bold text-gray-900">Financial Stress Level</h2>
          <div className="flex items-center gap-2">
            <span className={clsx("font-bold", textClass)}>{category}</span>
            <span className="text-gray-400 text-sm">| Score: {score.toFixed(0)}/100</span>
          </div>
        </div>
      </div>
      
      {/* Gauge bar */}
      <div className="w-full h-3 bg-gray-100 rounded-full mb-6 overflow-hidden flex">
        {/* Gradient mapping the 4 zones visually */}
        <div className="h-full bg-success-500 w-[30%]" title="Safe"></div>
        <div className="h-full bg-brand-500 w-[30%]" title="Comfortable"></div>
        <div className="h-full bg-warning-500 w-[20%]" title="Stretch"></div>
        <div className="h-full bg-danger-500 w-[20%]" title="Risky"></div>
        
        {/* The pointer */}
        <div 
          className="absolute h-5 w-1 bg-gray-900 -mt-1 rounded-sm shadow-md transition-all duration-500"
          style={{ left: `calc(${safeScore}% - 2px)` }}
        ></div>
      </div>

      <div className="bg-gray-50 rounded-lg p-4 border border-gray-100 text-sm text-gray-700 leading-relaxed">
        {explanation}
      </div>
    </div>
  );
}
