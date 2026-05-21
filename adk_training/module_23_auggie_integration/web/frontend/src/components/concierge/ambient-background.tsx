import { motion } from "framer-motion";

export function AmbientBackground() {
  return (
    <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
      {/* Gradient mesh */}
      <div className="absolute inset-0 bg-mesh opacity-90" />

      {/* Grid */}
      <div className="absolute inset-0 bg-grid opacity-50" />

      {/* Floating blobs */}
      <motion.div
        className="absolute -top-32 -left-32 h-[480px] w-[480px] rounded-full bg-cnc-azure/30 blur-[140px]"
        animate={{ x: [0, 60, -20, 0], y: [0, 40, -30, 0] }}
        transition={{ duration: 22, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="absolute top-40 -right-32 h-[520px] w-[520px] rounded-full bg-cnc-cyan/20 blur-[160px]"
        animate={{ x: [0, -60, 40, 0], y: [0, 80, -40, 0] }}
        transition={{ duration: 28, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="absolute bottom-0 left-1/3 h-[420px] w-[420px] rounded-full bg-cnc-electric/25 blur-[140px]"
        animate={{ x: [0, 50, -50, 0], y: [0, -40, 30, 0] }}
        transition={{ duration: 26, repeat: Infinity, ease: "easeInOut" }}
      />

      {/* Subtle horizontal scan line */}
      <div className="absolute inset-0 opacity-[0.04]">
        <div className="h-px w-full bg-gradient-to-r from-transparent via-cnc-cyan to-transparent animate-scan" />
      </div>
    </div>
  );
}
