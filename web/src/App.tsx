import { Route, Routes, useLocation } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { Layout } from "./components/Layout";
import Home from "./pages/Home";
import ConsultationPortal from "./pages/ConsultationPortal";
import PatientAnalysis from "./pages/PatientAnalysis";
import GenericBaseline from "./pages/GenericBaseline";
import VimleshTwin from "./pages/VimleshTwin";
import Comparison from "./pages/Comparison";
import Evidence from "./pages/Evidence";
import HistoricalCases from "./pages/HistoricalCases";
import GraphPage from "./pages/GraphPage";
import Insights from "./pages/Insights";
import Why from "./pages/Why";
import Explain from "./pages/Explain";
import Admin from "./pages/Admin";
import Studio from "./pages/Studio";
import { Card } from "./components/ui";

function Missing() {
  return <Card><h1 className="text-xl font-semibold">Page not found</h1></Card>;
}

export default function App() {
  const location = useLocation();
  return (
    <Layout>
      <AnimatePresence mode="wait">
        <motion.div key={location.pathname} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -6 }} transition={{ duration: 0.22 }}>
          <Routes location={location}>
            <Route path="/" element={<Home />} />
            <Route path="/consultation" element={<ConsultationPortal />} />
            <Route path="/patient" element={<PatientAnalysis />} />
            <Route path="/generic" element={<GenericBaseline />} />
            <Route path="/twin" element={<VimleshTwin />} />
            <Route path="/compare" element={<Comparison />} />
            <Route path="/evidence" element={<Evidence />} />
            <Route path="/cases" element={<HistoricalCases />} />
            <Route path="/graph" element={<GraphPage />} />
            <Route path="/insights" element={<Insights />} />
            <Route path="/why" element={<Why />} />
            <Route path="/explain" element={<Explain />} />
            <Route path="/admin" element={<Admin />} />
            <Route path="/studio" element={<Studio />} />
            <Route path="*" element={<Missing />} />
          </Routes>
        </motion.div>
      </AnimatePresence>
    </Layout>
  );
}
