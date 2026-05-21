import { motion } from "framer-motion";
import { X } from "lucide-react";

interface Props {
  open: boolean;
  url: string | null;
  title: string;
  onClose: () => void;
}

export function EvidencePlayer({ open, url, title, onClose }: Props) {
  if (!open || !url) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-cnc-bg/85 backdrop-blur-sm p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="relative w-full max-w-4xl rounded-2xl border border-cnc-line bg-cnc-surface/95 p-4 shadow-2xl"
      >
        <button
          onClick={onClose}
          className="absolute right-3 top-3 z-10 rounded-lg bg-cnc-bg/70 p-1.5 text-cnc-muted hover:bg-cnc-bg hover:text-white"
          aria-label="Close"
        >
          <X className="h-4 w-4" />
        </button>
        <div className="mb-2 pr-8 text-sm font-bold text-white">{title}</div>
        <video
          src={url}
          controls
          autoPlay
          className="aspect-video w-full rounded-xl border border-cnc-line bg-black"
        />
        <div className="mt-2 break-all text-xs font-mono text-cnc-muted">{url}</div>
      </motion.div>
    </div>
  );
}
