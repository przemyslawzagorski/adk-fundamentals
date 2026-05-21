import * as React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Info, ChevronDown, type LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

export interface HelpItem {
  icon?: LucideIcon;
  title: string;
  desc: string;
}

interface HelpPanelProps {
  /** Short title shown collapsed, e.g. "Co możesz tu zrobić?" */
  title?: string;
  /** One-paragraph elevator pitch for the view */
  summary: string;
  /** Bulleted feature list — what user can achieve here */
  items: HelpItem[];
  /** Optional callout footer, e.g. safety reminders */
  footer?: React.ReactNode;
  /** Default open? Defaults to false (less intrusive). */
  defaultOpen?: boolean;
  /** localStorage key — when set, open/closed state persists per user */
  storageKey?: string;
  className?: string;
}

/**
 * Reusable, professional contextual-help panel.
 *
 * Design decisions:
 * - Collapsed by default — power users are not interrupted.
 * - Open state can persist per-view via `storageKey` so the user only
 *   acknowledges the explainer once.
 * - Visual: glass card matching the rest of the concierge palette,
 *   no marketing fluff, no walls of text.
 */
export function HelpPanel({
  title = "Co możesz tu zrobić?",
  summary,
  items,
  footer,
  defaultOpen = false,
  storageKey,
  className,
}: HelpPanelProps) {
  const [open, setOpen] = React.useState(() => {
    if (typeof window === "undefined" || !storageKey) return defaultOpen;
    const v = window.localStorage.getItem(storageKey);
    return v === null ? defaultOpen : v === "1";
  });

  React.useEffect(() => {
    if (storageKey && typeof window !== "undefined") {
      window.localStorage.setItem(storageKey, open ? "1" : "0");
    }
  }, [open, storageKey]);

  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-2xl border border-cnc-border/70",
        "bg-gradient-to-br from-cnc-electric/5 via-cnc-surface/40 to-cnc-surface/10",
        "backdrop-blur-md shadow-card-up",
        className,
      )}
    >
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center gap-3 px-4 py-3 text-left transition-colors hover:bg-cnc-electric/5"
        aria-expanded={open}
      >
        <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-cnc-electric/15 text-cnc-electric2">
          <Info className="h-4 w-4" />
        </span>
        <span className="flex-1">
          <span className="block text-sm font-semibold text-white">{title}</span>
          <span className="block truncate text-xs text-cnc-muted">{summary}</span>
        </span>
        <ChevronDown
          className={cn(
            "h-4 w-4 shrink-0 text-cnc-muted transition-transform",
            open && "rotate-180",
          )}
        />
      </button>

      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            key="content"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25, ease: [0.2, 0.8, 0.2, 1] }}
            className="overflow-hidden"
          >
            <div className="space-y-4 border-t border-cnc-border/60 px-4 py-4">
              <p className="text-sm leading-relaxed text-cnc-ink">{summary}</p>

              <ul className="grid gap-2 sm:grid-cols-2">
                {items.map((it, i) => (
                  <li
                    key={i}
                    className="flex items-start gap-2.5 rounded-xl border border-cnc-border/50 bg-cnc-surface/50 p-3"
                  >
                    {it.icon && (
                      <span className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-cnc-cyan/15 text-cnc-cyan2">
                        <it.icon className="h-3.5 w-3.5" />
                      </span>
                    )}
                    <span>
                      <span className="block text-sm font-semibold text-white">{it.title}</span>
                      <span className="block text-xs leading-relaxed text-cnc-muted">{it.desc}</span>
                    </span>
                  </li>
                ))}
              </ul>

              {footer && (
                <div className="rounded-xl border border-cnc-gold/30 bg-cnc-gold/5 p-3 text-xs text-cnc-muted">
                  {footer}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
