import { motion } from "framer-motion";

/**
 * Pelnoekranowe ambientowe tlo: trzy gradient bloby + grid + scanlines.
 * Wszystko absolutnie pozycjonowane, pointer-events:none.
 */
export function AmbientBackground() {
  return (
    <div aria-hidden className="pointer-events-none absolute inset-0 overflow-hidden">
      {/* deep gradient mesh */}
      <div className="absolute inset-0 bg-mesh opacity-70" />

      {/* siatka */}
      <div className="absolute inset-0 bg-grid opacity-60" />

      {/* bloby */}
      <motion.div
        className="absolute -left-32 top-10 h-[520px] w-[520px] rounded-full bg-zagi-crimson/30 blur-[120px]"
        animate={{ x: [0, 60, -20, 0], y: [0, -40, 30, 0] }}
        transition={{ duration: 18, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="absolute -right-40 top-32 h-[600px] w-[600px] rounded-full bg-zagi-violet/25 blur-[140px]"
        animate={{ x: [0, -40, 20, 0], y: [0, 30, -20, 0] }}
        transition={{ duration: 22, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="absolute left-1/3 top-[60%] h-[400px] w-[400px] rounded-full bg-zagi-neon/20 blur-[120px]"
        animate={{ x: [0, 40, -30, 0], y: [0, -20, 40, 0] }}
        transition={{ duration: 26, repeat: Infinity, ease: "easeInOut" }}
      />

      {/* scanline subtle */}
      <div className="absolute inset-0 bg-[linear-gradient(transparent_50%,rgba(255,255,255,0.012)_50%)] bg-[length:100%_4px]" />

      {/* vignette */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_55%,#08090c_95%)]" />
    </div>
  );
}
