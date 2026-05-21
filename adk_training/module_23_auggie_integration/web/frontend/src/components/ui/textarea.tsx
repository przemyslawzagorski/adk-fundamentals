import * as React from "react";
import { cn } from "@/lib/utils";

export const Textarea = React.forwardRef<HTMLTextAreaElement, React.TextareaHTMLAttributes<HTMLTextAreaElement>>(
  ({ className, ...props }, ref) => (
    <textarea
      ref={ref}
      className={cn(
        "flex min-h-[120px] w-full rounded-xl border border-cnc-border bg-cnc-bg/60 px-4 py-3 text-sm font-mono text-cnc-ink placeholder:text-cnc-muted/60 transition-colors",
        "focus-visible:outline-none focus-visible:border-cnc-electric focus-visible:ring-2 focus-visible:ring-cnc-electric/30",
        "disabled:cursor-not-allowed disabled:opacity-50 resize-y",
        className,
      )}
      {...props}
    />
  ),
);
Textarea.displayName = "Textarea";
