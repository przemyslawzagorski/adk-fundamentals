import * as Icons from "lucide-react";
import { Sparkles } from "lucide-react";

export interface DynamicIconProps {
  name: string;
  className?: string;
  size?: number;
  strokeWidth?: number;
}

export function DynamicIcon({ name, className, size = 20, strokeWidth = 2 }: DynamicIconProps) {
  const Icon = (Icons as any)[name] ?? Sparkles;
  return <Icon className={className} size={size} strokeWidth={strokeWidth} />;
}
