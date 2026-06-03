import { Link } from 'react-router-dom';
import { ArrowRight, BarChart3, TrendingUp, ShieldCheck } from 'lucide-react';

export default function Home() {
  return (
    <div className="flex-1 bg-white">
      {/* Hero Section */}
      <div className="relative isolate px-6 pt-14 lg:px-8 bg-brand-50 border-b border-brand-100">
        <div className="mx-auto max-w-2xl py-24 sm:py-32 lg:py-40">
          <div className="text-center">
            <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl text-brand-700">
              Can you afford your dream home in India?
            </h1>
            <p className="mt-6 text-lg leading-8 text-gray-600">
              Plan your future property purchase using savings forecasts, housing market trends, inflation scenarios, and affordability analysis tailored for UAE expats.
            </p>
            <div className="mt-10 flex items-center justify-center gap-x-6">
              <Link
                to="/planner"
                className="rounded-md bg-brand-700 px-8 py-4 text-lg font-semibold text-white shadow-sm hover:bg-brand-800 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-600 flex items-center gap-2"
              >
                Start Planning <ArrowRight size={20} />
              </Link>
              <Link to="/insights" className="text-sm font-semibold leading-6 text-gray-900 hover:text-brand-700">
                View Recruiter Insights <span aria-hidden="true">→</span>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="mx-auto max-w-7xl px-6 py-24 sm:py-32 lg:px-8">
        <div className="mx-auto max-w-2xl lg:text-center">
          <h2 className="text-base font-semibold leading-7 text-brand-600">Smarter Planning</h2>
          <p className="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
            Data-driven real estate forecasting
          </p>
        </div>
        <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-4xl">
          <dl className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-10 lg:max-w-none lg:grid-cols-3 lg:gap-y-16">
            <div className="relative pl-16">
              <dt className="text-base font-semibold leading-7 text-gray-900">
                <div className="absolute left-0 top-0 flex h-10 w-10 items-center justify-center rounded-lg bg-brand-700">
                  <TrendingUp className="h-6 w-6 text-white" aria-hidden="true" />
                </div>
                Market Validated Scenarios
              </dt>
              <dd className="mt-2 text-base leading-7 text-gray-600">
                Extrapolations based on the official National Housing Bank HPI, capturing both pre-COVID trends and post-2022 appreciation.
              </dd>
            </div>
            <div className="relative pl-16">
              <dt className="text-base font-semibold leading-7 text-gray-900">
                <div className="absolute left-0 top-0 flex h-10 w-10 items-center justify-center rounded-lg bg-brand-700">
                  <BarChart3 className="h-6 w-6 text-white" aria-hidden="true" />
                </div>
                AED-INR FX Projection
              </dt>
              <dd className="mt-2 text-base leading-7 text-gray-600">
                Currency tailwind analysis utilizing Facebook Prophet to forecast the long-term depreciation trajectory of the Rupee.
              </dd>
            </div>
            <div className="relative pl-16">
              <dt className="text-base font-semibold leading-7 text-gray-900">
                <div className="absolute left-0 top-0 flex h-10 w-10 items-center justify-center rounded-lg bg-brand-700">
                  <ShieldCheck className="h-6 w-6 text-white" aria-hidden="true" />
                </div>
                Financial Stress Score
              </dt>
              <dd className="mt-2 text-base leading-7 text-gray-600">
                A deterministic engine that grades the risk of your goal based on coverage shortfall, expense burden, and goal gap.
              </dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  );
}
