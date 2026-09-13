import { renderKatex } from "@/lib/katex";
import { cn } from "@/lib/utils";

export function Equation({
  latex,
  plain,
  caption,
  display = true,
}: {
  latex: string;
  plain?: string;
  caption?: string;
  display?: boolean;
}) {
  const { html, error } = renderKatex(latex, display);
  return (
    <figure className="my-3">
      {html ? (
        <div
          className={cn("overflow-x-auto text-ink", display && "text-center")}
          dangerouslySetInnerHTML={{ __html: html }}
        />
      ) : (
        <pre className="overflow-x-auto rounded-md bg-surface-2 p-3 text-sm">{plain || latex}</pre>
      )}
      {error ? (
        <p role="status" className="mt-1 text-sm text-warn">
          Notation could not be rendered. Showing the plain form instead. {error}
        </p>
      ) : null}
      {caption ? <figcaption className="mt-1 text-sm text-muted">{caption}</figcaption> : null}
    </figure>
  );
}
