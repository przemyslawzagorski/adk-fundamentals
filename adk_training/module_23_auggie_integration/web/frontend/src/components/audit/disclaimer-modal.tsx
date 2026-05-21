import * as React from "react";
import { motion } from "framer-motion";
import { ShieldAlert, X } from "lucide-react";
import { Button } from "@/components/ui/button";

interface Props {
  open: boolean;
  targetUrl: string;
  onAccept: () => void;
  onCancel: () => void;
}

export function DisclaimerModal({ open, targetUrl, onAccept, onCancel }: Props) {
  const [checked, setChecked] = React.useState(false);
  React.useEffect(() => {
    if (!open) setChecked(false);
  }, [open]);
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-cnc-bg/80 backdrop-blur-sm p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        className="relative w-full max-w-lg rounded-2xl border border-cnc-rose/40 bg-cnc-surface/95 p-6 shadow-2xl"
      >
        <button
          onClick={onCancel}
          className="absolute right-4 top-4 rounded-lg p-1.5 text-cnc-muted hover:bg-cnc-surface2 hover:text-white"
          aria-label="Close"
        >
          <X className="h-4 w-4" />
        </button>
        <div className="mb-4 flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-cnc-rose/15 text-cnc-rose">
            <ShieldAlert className="h-6 w-6" />
          </div>
          <div>
            <h2 className="text-xl font-extrabold text-white">Legal authorization required</h2>
            <p className="text-xs text-cnc-muted">Penetration testing without consent is illegal in most jurisdictions.</p>
          </div>
        </div>
        <div className="mb-4 rounded-xl border border-cnc-line bg-cnc-bg/60 p-4 text-sm text-cnc-ink">
          <p className="mb-2">
            You are about to perform <strong className="text-cnc-rose">active security testing</strong> on:
          </p>
          <p className="break-all rounded-md border border-cnc-line bg-cnc-surface/60 px-3 py-2 font-mono text-xs text-cnc-cyan2">
            {targetUrl}
          </p>
        </div>
        <label className="mb-4 flex items-start gap-3 rounded-xl border border-cnc-line bg-cnc-bg/40 p-3 text-xs text-cnc-ink hover:border-cnc-electric/60">
          <input
            type="checkbox"
            checked={checked}
            onChange={(e) => setChecked(e.target.checked)}
            className="mt-0.5 h-4 w-4 cursor-pointer accent-cnc-electric"
          />
          <span>
            I confirm I have <strong>explicit written authorization</strong> from the target system owner to
            perform security testing. I accept full legal responsibility for this audit and will use
            findings only to improve security.
          </span>
        </label>
        <div className="flex justify-end gap-2">
          <Button variant="ghost" onClick={onCancel}>Cancel</Button>
          <Button
            variant="destructive"
            disabled={!checked}
            onClick={onAccept}
          >
            I authorize this audit
          </Button>
        </div>
      </motion.div>
    </div>
  );
}
