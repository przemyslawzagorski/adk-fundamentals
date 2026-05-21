import * as React from "react";
import { cn } from "@/lib/utils";

export const Input = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  ({ className, type, ...props }, ref) => (
    <input
      type={type}
      ref={ref}
      className={cn(
        "flex h-11 w-full rounded-xl border border-cnc-border bg-cnc-bg/60 px-4 py-2 text-sm text-cnc-ink placeholder:text-cnc-muted/70 transition-colors",
        "focus-visible:outline-none focus-visible:border-cnc-electric focus-visible:ring-2 focus-visible:ring-cnc-electric/30",
        "disabled:cursor-not-allowed disabled:opacity-50",
        className,
      )}
      {...props}
    />
  ),
);
Input.displayName = "Input";
