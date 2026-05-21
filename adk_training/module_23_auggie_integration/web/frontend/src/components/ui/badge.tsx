import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors",
  {
    variants: {
      variant: {
        default: "border-cnc-electric/30 bg-cnc-electric/15 text-cnc-electric2",
        cyan: "border-cnc-cyan/30 bg-cnc-cyan/15 text-cnc-cyan2",
        azure: "border-cnc-azure/40 bg-cnc-azure/20 text-cnc-electric2",
        outline: "border-cnc-line text-cnc-muted",
        success: "border-emerald-500/30 bg-emerald-500/15 text-emerald-400",
        warning: "border-cnc-gold/40 bg-cnc-gold/15 text-cnc-gold",
        danger: "border-cnc-rose/40 bg-cnc-rose/15 text-cnc-rose",
        muted: "border-cnc-border bg-cnc-surface text-cnc-muted",
      },
    },
    defaultVariants: { variant: "default" },
  },
);

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement>, VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <span className={cn(badgeVariants({ variant }), className)} {...props} />;
}
