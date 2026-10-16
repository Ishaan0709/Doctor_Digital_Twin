import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { DataTable } from "../components/DataTable";
import { Button, Card, Note, PageHeader, Skeleton } from "../components/ui";
import { postJson } from "../lib/api";
import { useAppStore } from "../store/useAppStore";
import type { CaseMatch } from "../types";

export default function HistoricalCases() {
  const patient = useAppStore((s) => s.patient);
  const navigate = useNavigate();
  const [rows, setRows] = useState<CaseMatch[] | null>(null);

  useEffect(() => {
    if (!patient) return;
    postJson<{ matches: CaseMatch[] }>("/api/evidence/cases", patient)
      .then((data) => setRows(data.matches))
      .catch((error: Error) => toast.error(error.message));
  }, [patient]);

  if (!patient) return <Card><p>Please complete Patient Intake first.</p><Link to="/patient" className="text-sky-600">Open intake</Link></Card>;
  return (
    <div>
      <PageHeader eyebrow="6 · Cases" title="Historical Case Intelligence" caption="Top similar historical specialist cardiology cases." />
      <Note title="How to use these matches">These cases are evidence references for similar symptom-risk patterns. They should not override the current patient.</Note>
      {rows === null && <Skeleton className="h-48" />}
      {rows && rows.length === 0 && <Card>No cases retrieved yet.</Card>}
      {rows && rows.length > 0 && (
        <DataTable
          rows={rows as unknown as Record<string, unknown>[]}
          searchKeys={["case_id", "diagnosis", "symptoms", "decision", "outcome"]}
          filterKey="diagnosis"
          columns={[
            { key: "case_id", label: "Case" },
            { key: "match_score", label: "Similarity", render: (row) => Number(row.match_score || 0).toFixed(2) },
            { key: "diagnosis", label: "Diagnosis" },
            { key: "decision", label: "Decision" },
            { key: "outcome", label: "Outcome" },
          ]}
          expand={(row) => (
            <div className="space-y-1 text-sm">
              <p><strong>Symptoms:</strong> {String(row.symptoms || "NA")}</p>
              <p><strong>Risk factors:</strong> {String(row.risk_factors || "NA")}</p>
              <p><strong>Tests:</strong> {String(row.tests || "NA")}</p>
              <p title="FAISS cosine similarity between the current patient embedding and the case embedding.">Similarity is the FAISS cosine score. 1.00 is very close.</p>
            </div>
          )}
        />
      )}
      <Button className="mt-4" variant="primary" onClick={() => navigate("/graph")}>Open Graph Intelligence</Button>
    </div>
  );
}
