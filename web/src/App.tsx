import { Route, Routes, useLocation } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { Layout } from "./components/Layout";
import Home from "./pages/Home";
import ConsultationPortal from "./pages/ConsultationPortal";
import Comparison from "./pages/Comparison";
import GraphPage from "./pages/GraphPage";
import Records from "./pages/Records";
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
            <Route path="/records" element={<Records />} />
            <Route path="/compare" element={<Comparison />} />
            <Route path="/graph" element={<GraphPage />} />
            <Route path="*" element={<Missing />} />
          </Routes>
        </motion.div>
      </AnimatePresence>
    </Layout>
  );
}
