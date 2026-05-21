import { Routes, Route, useLocation } from "react-router-dom";
import { AnimatePresence } from "framer-motion";
import { Navbar } from "@/components/concierge/navbar";
import { ErrorBoundary } from "@/components/concierge/error-boundary";
import { Landing } from "@/pages/Landing";
import { Studio } from "@/pages/Studio";
import { Audit } from "@/pages/Audit";
import { Analyst } from "@/pages/Analyst";
import { Knowledge } from "@/pages/Knowledge";
import { HistoryPage } from "@/pages/History";

export default function App() {
  const location = useLocation();
  return (
    <div className="relative min-h-screen overflow-x-hidden">
      <Navbar />
      <ErrorBoundary>
        <AnimatePresence mode="wait">
          <Routes location={location} key={location.pathname}>
            <Route path="/" element={<Landing />} />
            <Route path="/studio" element={<Studio />} />
            <Route path="/audit" element={<Audit />} />
            <Route path="/analyst" element={<Analyst />} />
            <Route path="/knowledge" element={<Knowledge />} />
            <Route path="/history" element={<HistoryPage />} />
            <Route path="*" element={<Landing />} />
          </Routes>
        </AnimatePresence>
      </ErrorBoundary>
    </div>
  );
}
