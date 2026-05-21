import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-xl text-sm font-semibold transition-all duration-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cnc-electric/60 focus-visible:ring-offset-2 focus-visible:ring-offset-cnc-bg disabled:pointer-events-none disabled:opacity-50 active:scale-[0.97]",
  {
    variants: {
      variant: {
        default:
          "bg-azure-grad text-white shadow-glow hover:shadow-glow-cyan hover:brightness-110 animate-gradient",
        outline:
          "border border-cnc-line bg-cnc-surface/40 text-cnc-ink hover:bg-cnc-surface hover:border-cnc-electric/60 hover:text-white",
        ghost:
          "text-cnc-muted hover:bg-cnc-surface/60 hover:text-cnc-ink",
        secondary:
          "bg-cnc-surface text-cnc-ink hover:bg-cnc-surface2 border border-cnc-border",
        destructive:
          "bg-cnc-rose/90 text-white hover:bg-cnc-rose shadow-glow-sm",
        link: "text-cnc-electric2 underline-offset-4 hover:underline hover:text-cnc-cyan",
        accent:
          "bg-cnc-cyan text-cnc-bg font-bold shadow-glow-cyan hover:bg-cnc-cyan2",
      },
      size: {
        default: "h-11 px-5",
        sm: "h-9 px-4 text-xs",
        lg: "h-14 px-8 text-base",
        xl: "h-16 px-10 text-lg",
        icon: "h-11 w-11",
      },
    },
    defaultVariants: { variant: "default", size: "default" },
  },
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return <Comp className={cn(buttonVariants({ variant, size, className }))} ref={ref} {...props} />;
  },
);
Button.displayName = "Button";
