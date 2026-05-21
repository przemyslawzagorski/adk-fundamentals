import { motion } from "framer-motion";

interface Props {
  size?: number;
  withWordmark?: boolean;
  className?: string;
}

export function ZagiLogo({ size = 32, withWordmark = false, className }: Props) {
  return (
    <div className={`flex items-center gap-2.5 ${className ?? ""}`}>
      <motion.svg
        width={size}
        height={size}
        viewBox="0 0 64 64"
        initial={{ rotate: -8, opacity: 0 }}
        animate={{ rotate: 0, opacity: 1 }}
        transition={{ type: "spring", stiffness: 200, damping: 15 }}
        className="drop-shadow-[0_0_18px_rgba(229,9,20,0.55)]"
      >
        <defs>
          <linearGradient id="zagi-g" x1="0" y1="0" x2="64" y2="64" gradientUnits="userSpaceOnUse">
            <stop offset="0" stopColor="#ff1f3d" />
            <stop offset="0.6" stopColor="#e50914" />
            <stop offset="1" stopColor="#a78bfa" />
          </linearGradient>
        </defs>
        <rect width="64" height="64" rx="14" fill="#0f1115" stroke="#1f232b" />
        <path
          d="M18 16 L46 16 L22 48 L46 48"
          stroke="url(#zagi-g)"
          strokeWidth="6"
          fill="none"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <motion.circle
          cx="46"
          cy="16"
          r="4"
          fill="#5eead4"
          animate={{ scale: [1, 1.3, 1], opacity: [1, 0.7, 1] }}
          transition={{ duration: 2.4, repeat: Infinity, ease: "easeInOut" }}
        />
      </motion.svg>
      {withWordmark && (
        <div className="flex flex-col leading-none">
          <span className="text-lg font-extrabold tracking-tight text-white">
            ZAGI
          </span>
          <span className="text-[9px] font-medium uppercase tracking-[0.2em] text-zagi-muted">
            Spec Intelligence
          </span>
        </div>
      )}
    </div>
  );
}
