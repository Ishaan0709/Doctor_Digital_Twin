import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { streamConsult } from "../lib/api";
import { useAppStore } from "../store/useAppStore";
import type { TwinResult } from "../types";
import { BulletList, Button, Card, Confidence, Disclaimer, Note, PageHeader, Skeleton, SourceList } from "../components/ui";

export default function VimleshTwin() {
  const patient = useAppStore((s) => s.patient);
  const saved = useAppStore((s) => s.twinResult);
  const setTwin = useAppStore((s) => s.setTwinResult);
  const navigate = useNavigate();
  const [live, setLive] = useState("");
  const [meta, setMeta] = useState<TwinResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [run, setRun] = useState(0);

  useEffect(() => {
    if (!patient || (saved && run === 0)) return;
    const ctrl = new AbortController();
    let acc = "";
    let received: TwinResult | null = null;
    setLoading(true);
    setLive("");
    streamConsult({ kind: "twin", patient }, (event) => {
      if (event.type === "meta" && event.result) {
        received = event.result as TwinResult;
        setMeta(received);
      }
      if (event.type === "token" && event.text) {
        acc += event.text;
        setLive(acc);
      }
      if (event.type === "done" && received) setTwin({ ...received, assessment: event.text || acc });
    }, ctrl.signal).catch((error: Error) => {
      if (error.name !== "AbortError") toast.error(error.message);
    }).finally(() => setLoading(false));
    return () => ctrl.abort();
  }, [patient, run, saved, setTwin]);

  if (!patient) return <Card><p>Please complete Patient Intake first.</p><Link className="mt-3 inline-block text-sky-600" to="/patient">Open Patient Analysis</Link></Card>;
  const result = saved || (meta ? { ...meta, assessment: live } : null);
  return (
    <div>
      <PageHeader eyebrow="3 · Twin" title="Dr. Vimlesh Pandey Specialist Twin" caption="Patient-first specialist reasoning powered by historical RAG and GraphRAG evidence." />
      <div className="mb-4 flex items-center gap-4">
        <img src="/doctor_photo.png" alt="Dr. Vimlesh Pandey" className="h-16 w-16 rounded-2xl object-cover" />
        <Note title="How to read this page">Assessment is generated with current patient priority, then enriched with similar historical patterns and graph relationships. Historical cases are references, not copy-paste prescriptions.</Note>
      </div>
      {!result && loading && <Skeleton className="h-48" />}
      {result && (
        <div className="space-y-4">
          <Card>
            <h2 className="font-semibold">Specialist assessment</h2>
            <p className="mt-3 whitespace-pre-wrap text-sm leading-7">{result.assessment || (loading ? "Writing…" : "")}</p>
            {!!result.clarifying_questions?.length && (
              <div className="mt-4"><h3 className="text-sm font-semibold">Clarifying questions</h3><BulletList items={result.clarifying_questions} /></div>
            )}
            <SourceList sources={result.sources} />
            <Disclaimer text={result.disclaimer} />
          </Card>
          <div className="grid gap-4 md:grid-cols-2">
            <Card><h2 className="font-semibold">Why this patient is unique</h2><div className="mt-3"><BulletList items={result.unique_factors} /></div></Card>
            <Card>
              <h2 className="font-semibold">Historical patterns considered</h2>
              <ul className="mt-3 space-y-2 text-sm">
                {result.historical_patterns?.map((item) => (
                  <li key={String(item.case_id)} title="Final similarity = base FAISS cosine score + rerank bonus from symptom and diagnosis overlap.">
                    Case {item.case_id}: {item.diagnosis} <span className="text-sky-600 dark:text-sky-300">(similarity {Number(item.final_match_score ?? item.match_score ?? 0).toFixed(2)})</span>
                  </li>
                ))}
              </ul>
            </Card>
          </div>
          <div className="grid gap-4 md:grid-cols-3">
            <Card><h2 className="font-semibold">Recommended tests</h2><div className="mt-3"><BulletList items={result.recommended_tests} /></div></Card>
            <Card><h2 className="font-semibold">Immediate actions</h2><div className="mt-3"><BulletList items={result.immediate_actions} /></div></Card>
            <Card><h2 className="font-semibold">Follow-up plan</h2><div className="mt-3"><BulletList items={result.follow_up_plan} /></div></Card>
          </div>
          <Confidence result={result} />
        </div>
      )}
      <div className="mt-4 flex flex-wrap gap-3">
        <Button variant="primary" onClick={() => navigate("/compare")}>Open GPT vs Twin Difference</Button>
        <Button onClick={() => { setTwin(null); setMeta(null); setRun((n) => n + 1); }}>Regenerate</Button>
      </div>
    </div>
  );
}
