export function KineticDiagram() {
  return (
    <svg viewBox="0 0 280 90" role="img" aria-label="Point mass with a velocity arrow" className="h-24 w-full max-w-sm">
      <circle cx="70" cy="45" r="16" fill="#0f766e" />
      <text x="70" y="50" textAnchor="middle" fill="white" fontSize="12">
        m
      </text>
      <line x1="90" y1="45" x2="210" y2="45" stroke="#1b2430" strokeWidth="2" />
      <polygon points="210,38 230,45 210,52" fill="#1b2430" />
      <text x="150" y="32" textAnchor="middle" fontSize="12" fill="#5b6570">
        v
      </text>
    </svg>
  );
}

export function SpringDiagram() {
  return (
    <svg viewBox="0 0 280 90" role="img" aria-label="Wall, spring, and mass with displacement" className="h-24 w-full max-w-sm">
      <rect x="8" y="18" width="10" height="54" fill="#1b2430" />
      <polyline
        points="18,45 34,28 50,62 66,28 82,62 98,28 114,45"
        fill="none"
        stroke="#0f766e"
        strokeWidth="3"
      />
      <rect x="114" y="30" width="36" height="30" fill="#0f766e" />
      <line x1="150" y1="45" x2="220" y2="45" stroke="#b45309" strokeDasharray="4 3" />
      <text x="186" y="38" fontSize="12" fill="#b45309">
        x
      </text>
    </svg>
  );
}

export function RcDiagram() {
  return (
    <svg viewBox="0 0 280 110" role="img" aria-label="Simplified resistor-capacitor circuit" className="h-28 w-full max-w-sm">
      <rect x="30" y="20" width="70" height="28" fill="none" stroke="#1b2430" strokeWidth="2" />
      <text x="65" y="38" textAnchor="middle" fontSize="12">
        R
      </text>
      <line x1="100" y1="34" x2="190" y2="34" stroke="#1b2430" />
      <line x1="190" y1="18" x2="190" y2="50" stroke="#0f766e" strokeWidth="3" />
      <line x1="206" y1="18" x2="206" y2="50" stroke="#0f766e" strokeWidth="3" />
      <text x="198" y="70" textAnchor="middle" fontSize="12">
        C
      </text>
      <line x1="206" y1="34" x2="250" y2="34" stroke="#1b2430" />
      <line x1="30" y1="90" x2="250" y2="90" stroke="#1b2430" />
      <line x1="30" y1="48" x2="30" y2="90" stroke="#1b2430" />
      <line x1="250" y1="34" x2="250" y2="90" stroke="#1b2430" />
    </svg>
  );
}

export function NumberLineDiagram({ highlight = 0.5 }: { highlight?: number }) {
  const x = 40 + highlight * 200;
  return (
    <svg viewBox="0 0 280 70" role="img" aria-label="Number line with a highlighted counterexample interval" className="h-20 w-full max-w-sm">
      <line x1="20" y1="36" x2="260" y2="36" stroke="#1b2430" />
      <polygon points="260,30 272,36 260,42" fill="#1b2430" />
      <circle cx={x} cy="36" r="7" fill="#b91c1c" />
      <text x={x} y="58" textAnchor="middle" fontSize="11" fill="#b91c1c">
        {highlight}
      </text>
      <text x="40" y="22" fontSize="11" fill="#5b6570">
        0
      </text>
      <text x="240" y="22" fontSize="11" fill="#5b6570">
        1
      </text>
    </svg>
  );
}

export function InvestigationDiagram({ id }: { id: string }) {
  if (id.includes("spring") || id.includes("oscillator") || id.includes("damped")) return <SpringDiagram />;
  if (id.includes("rc")) return <RcDiagram />;
  if (id.includes("counterexample") || id.includes("domain") || id.includes("contradiction")) {
    return <NumberLineDiagram />;
  }
  return <KineticDiagram />;
}
