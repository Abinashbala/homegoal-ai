import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { PlannerProvider } from './context/PlannerContext';

import Navbar from './components/layout/Navbar';
import Home from './pages/Home';
import Planner from './pages/Planner';
import Results from './pages/Results';
import ScenarioAnalysis from './pages/ScenarioAnalysis';
import RecruiterInsights from './pages/RecruiterInsights';

function App() {
  return (
    <PlannerProvider>
      <BrowserRouter>
        <div className="min-h-screen bg-gray-50 flex flex-col font-sans text-gray-900">
          <Navbar />
          <main className="flex-grow flex flex-col">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/planner" element={<Planner />} />
              <Route path="/results" element={<Results />} />
              <Route path="/scenarios" element={<ScenarioAnalysis />} />
              <Route path="/insights" element={<RecruiterInsights />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </PlannerProvider>
  );
}

export default App;
