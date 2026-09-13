import type { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

export function Badge({
  className,
  tone = "muted",
  ...props
}: HTMLAttributes<HTMLSpanElement> & { tone?: "ok" | "bad" | "warn" | "info" | "muted" }) {
  const tones = {
    ok: "bg-green-50 text-ok",
    bad: "bg-red-50 text-bad",
    warn: "bg-amber-50 text-warn",
    info: "bg-sky-50 text-info",
    muted: "bg-surface-2 text-muted",
  };
  return (
    <span
      className={cn("inline-flex rounded-full px-2.5 py-0.5 text-xs font-semibold", tones[tone], className)}
      {...props}
    />
  );
}
