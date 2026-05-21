import { Routes, Route, useLocation } from "react-router-dom";
import { AnimatePresence } from "framer-motion";
import { ToastProvider } from "@/components/toast";
import { Navbar } from "@/components/zagi/navbar";
import { Landing } from "@/pages/Landing";
import { Studio } from "@/pages/Studio";

export default function App() {
  const location = useLocation();
  return (
    <ToastProvider>
      <div className="relative min-h-screen overflow-x-hidden">
        <Navbar />
        <AnimatePresence mode="wait">
          <Routes location={location} key={location.pathname}>
            <Route path="/" element={<Landing />} />
            <Route path="/studio" element={<Studio />} />
            <Route path="*" element={<Landing />} />
          </Routes>
        </AnimatePresence>
      </div>
    </ToastProvider>
  );
}
