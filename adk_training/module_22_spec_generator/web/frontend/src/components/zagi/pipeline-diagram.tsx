import { motion } from "framer-motion";
import {
  Ticket,
  Network,
  PenLine,
  RefreshCw,
  ListTree,
} from "lucide-react";

const NODES = [
  { key: "ticket",  icon: Ticket,   label: "Jira",     desc: "Fetch" },
  { key: "context", icon: Network,  label: "Context",  desc: "Wiki + Code + NLM" },
  { key: "hld",     icon: PenLine,  label: "HLD",      desc: "Gemini writer" },
  { key: "loop",    icon: RefreshCw,label: "Critique", desc: "Loop x N" },
  { key: "epics",   icon: ListTree, label: "Epics",    desc: "Decompose" },
];

/**
 * Animowany horyzontalny pipeline 5 nodow z plynacymi liniami.
 * Self-contained - nie zalezy od stanu API.
 */
export function PipelineDiagram() {
  return (
    <div className="relative w-full overflow-hidden rounded-2xl glass-strong p-6">
      {/* pulsujaca linia tla */}
      <div className="pointer-events-none absolute inset-x-6 top-1/2 -z-10 h-px -translate-y-1/2 bg-gradient-to-r from-transparent via-zagi-crimson/40 to-transparent" />

      <div className="grid grid-cols-5 items-center gap-4">
        {NODES.map((node, idx) => (
          <motion.div
            key={node.key}
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ delay: idx * 0.12, duration: 0.5, ease: "easeOut" }}
            className="relative flex flex-col items-center gap-2"
          >
            <motion.div
              className="relative grid h-14 w-14 place-items-center rounded-2xl border border-white/10 bg-zagi-surface2 shadow-card-up"
              animate={{
                boxShadow: [
                  "0 0 0 0 rgba(229,9,20,0)",
                  "0 0 28px -2px rgba(229,9,20,0.55)",
                  "0 0 0 0 rgba(229,9,20,0)",
                ],
              }}
              transition={{
                duration: 2.4,
                repeat: Infinity,
                delay: idx * 0.4,
                ease: "easeInOut",
              }}
            >
              <node.icon className="h-6 w-6 text-zagi-neon" />
              <span className="absolute -right-1 -top-1 grid h-5 w-5 place-items-center rounded-full bg-zagi-crimson text-[10px] font-bold text-white">
                {idx + 1}
              </span>
            </motion.div>
            <div className="text-center">
              <div className="text-xs font-semibold text-white">{node.label}</div>
              <div className="text-[10px] uppercase tracking-wider text-zagi-muted">
                {node.desc}
              </div>
            </div>

            {idx < NODES.length - 1 && (
              <ArrowFlow delay={idx * 0.4} />
            )}
          </motion.div>
        ))}
      </div>
    </div>
  );
}

function ArrowFlow({ delay }: { delay: number }) {
  return (
    <div className="pointer-events-none absolute -right-2 top-7 hidden h-px w-6 overflow-hidden md:block">
      <motion.div
        className="h-full w-3 bg-gradient-to-r from-transparent via-zagi-crimson to-transparent"
        animate={{ x: ["-100%", "300%"] }}
        transition={{ duration: 1.6, repeat: Infinity, delay, ease: "linear" }}
      />
    </div>
  );
}
