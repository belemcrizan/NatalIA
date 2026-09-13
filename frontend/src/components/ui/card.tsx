import type { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("rounded-[var(--radius-md)] border border-line bg-surface shadow-[var(--shadow-card)]", className)}
      {...props}
    />
  );
}
