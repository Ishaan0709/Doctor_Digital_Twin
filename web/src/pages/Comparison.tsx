import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { streamConsult } from "../lib/api";
import { useAppStore } from "../store/useAppStore";
import type { TwinResult } from "../types";
import { Button, Card, Note, PageHeader, Skeleton } from "../components/ui";

export default function Comparison() {
  const patient = useAppStore((s) => s.patient);
  const generic = useAppStore((s) => s.genericResult);
  const twin = useAppStore((s) => s.twinResult);
  const setTwin = useAppStore((s) => s.setTwinResult);
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!patient || !generic || twin) return;
    const ctrl = new AbortController();
    let received: TwinResult | null = null;
    let acc = "";
    setLoading(true);
    streamConsult({ kind: "twin", patient }, (event) => {
      if (event.type === "meta" && event.result) received = event.result as TwinResult;
      if (event.type === "token" && event.text) acc += event.text;
      if (event.type === "done" && received) setTwin({ ...received, assessment: event.text || acc });
    }, ctrl.signal).catch((error: Error) => {
      if (error.name !== "AbortError") toast.error(error.message);
    }).finally(() => setLoading(false));
    return () => ctrl.abort();
  }, [patient, generic, twin, setTwin]);

  if (!patient) return <Card><p>Please complete Patient Intake first.</p><Link to="/patient" className="text-sky-600">Open intake</Link></Card>;
  if (!generic) return <Card><p>Please run the generic consultation first.</p><Link to="/generic" className="text-sky-600">Open generic baseline</Link></Card>;
  if (!twin || loading) return <Skeleton className="h-64" />;
  const links = twin.graph_evidence?.links?.length || 0;
  return (
    <div>
      <PageHeader eyebrow="4 · Difference" title="GPT vs Twin Diagnosis Difference" caption="Side-by-side view of baseline AI and specialist twin reasoning." />
      <Note title="How to read this comparison">The left side is generic AI from the current patient only. The right side is the Dr. Pandey twin using patient context, retrieved cases, and graph reasoning.</Note>
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <h2 className="text-xl font-semibold">Generic GPT</h2>
          <p className="mt-3 whitespace-pre-wrap text-sm leading-7">{generic.consultation_summary}</p>
          <ul className="mt-4 list-disc space-y-1 pl-5 text-sm"><li>Uses only direct patient text.</li><li>Does not reference specialist case memory.</li><li>Does not apply graph relationship reasoning.</li></ul>
        </Card>
        <Card>
          <h2 className="text-xl font-semibold">Dr. Pandey AI Twin</h2>
          <p className="mt-3 whitespace-pre-wrap text-sm leading-7">{twin.assessment}</p>
          <ul className="mt-4 list-disc space-y-1 pl-5 text-sm"><li>Uses patient-first specialist framing.</li><li>Adds retrieved historical case patterns.</li><li>Adds GraphRAG links for risk and decision context.</li></ul>
        </Card>
      </div>
      <div className="mt-4 grid gap-3 md:grid-cols-3">
        <Card><p className="text-sm text-slate-500">Historical cases used</p><p className="text-3xl font-semibold">{twin.historical_patterns?.length || 0}</p></Card>
        <Card><p className="text-sm text-slate-500">Graph links triggered</p><p className="text-3xl font-semibold">{links}</p></Card>
        <Card><p className="text-sm text-slate-500">Twin confidence</p><p className="text-3xl font-semibold">{Math.round((twin.confidence_score || 0) * 100)}%</p><p className="text-xs text-slate-500">min(0.98, 0.60 + 0.07×cases + 0.03×graph links)</p></Card>
      </div>
      <Button className="mt-4" variant="primary" onClick={() => navigate("/evidence")}>Continue to Evidence Center</Button>
    </div>
  );
}
