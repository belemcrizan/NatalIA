import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { useState } from "react";

import { AppShell } from "@/components/layout/AppShell";
import { identityGeneration } from "@/lib/api";
import { BenchmarkPage } from "@/pages/BenchmarkPage";
import { BuilderPage } from "@/pages/BuilderPage";
import { DiagnosticsPage } from "@/pages/DiagnosticsPage";
import { HistoryPage } from "@/pages/HistoryPage";
import { HomePage } from "@/pages/HomePage";
import { InvestigationPage } from "@/pages/InvestigationPage";
import { LibraryPage } from "@/pages/LibraryPage";
import { RunPage } from "@/pages/RunPage";
import { TrustPage } from "@/pages/TrustPage";

export default function App() {
  const [client] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: { staleTime: 10_000, retry: 1 },
        },
      }),
  );
  void identityGeneration;
  return (
    <QueryClientProvider client={client}>
      <BrowserRouter>
        <Routes>
          <Route element={<AppShell />}>
            <Route path="/" element={<HomePage />} />
            <Route path="/library" element={<LibraryPage />} />
            <Route path="/investigate/:id" element={<InvestigationPage />} />
            <Route path="/builder" element={<BuilderPage />} />
            <Route path="/history" element={<HistoryPage />} />
            <Route path="/history/:id" element={<RunPage />} />
            <Route path="/benchmark" element={<BenchmarkPage />} />
            <Route path="/trust" element={<TrustPage />} />
            <Route path="/diagnostics" element={<DiagnosticsPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
