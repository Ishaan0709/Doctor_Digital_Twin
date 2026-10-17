import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { streamConsult } from "../lib/api";
import { useAppStore } from "../store/useAppStore";
import type { GenericResult } from "../types";
import { RichText } from "../components/RichText";
import { BulletList, Button, Card, Disclaimer, Note, PageHeader, Skeleton, SourceList } from "../components/ui";

export default function GenericBaseline() {
  const patient = useAppStore((s) => s.patient);
  const saved = useAppStore((s) => s.genericResult);
  const setGeneric = useAppStore((s) => s.setGenericResult);
  const navigate = useNavigate();
  const [live, setLive] = useState("");
  const [meta, setMeta] = useState<GenericResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [run, setRun] = useState(0);

  useEffect(() => {
    if (!patient || (saved && run === 0)) return;
    const ctrl = new AbortController();
    let acc = "";
    let received: GenericResult | null = null;
    setLoading(true);
    setLive("");
    streamConsult({ kind: "generic", patient }, (event) => {
      if (event.type === "meta" && event.result) {
        received = event.result;
        setMeta(event.result);
      }
      if (event.type === "token" && event.text) {
        acc += event.text;
        setLive(acc);
      }
      if (event.type === "done" && received) setGeneric({ ...received, consultation_summary: event.text || acc });
    }, ctrl.signal).catch((error: Error) => {
      if (error.name !== "AbortError") toast.error(error.message);
    }).finally(() => setLoading(false));
    return () => ctrl.abort();
  }, [patient, run, saved, setGeneric]);

  if (!patient) {
    return <Card><p>Please complete Patient Intake first.</p><Link className="mt-3 inline-block text-sky-600" to="/patient">Open Patient Analysis</Link></Card>;
  }
  const result = saved || (meta ? { ...meta, consultation_summary: live } : null);
  return (
    <div>
      <PageHeader eyebrow="2 · Generic" title="Generic GPT Clinical Baseline" caption="Initial reasoning generated from the current patient profile only." />
      <Note title="Interpretation note">This baseline does not use Dr. Pandey's historical case memory or graph evidence. Use it as a neutral reference before specialist-twin reasoning.</Note>
      {!result && loading && <div className="space-y-3"><Skeleton className="h-40" /><Skeleton className="h-24" /></div>}
      {result && (
        <div className="grid gap-4 lg:grid-cols-[1.3fr_0.7fr]">
          <Card>
            <h2 className="font-semibold">Generic model summary</h2>
            {result.consultation_summary ? <RichText text={result.consultation_summary} /> : loading ? <p className="mt-3 text-sm">Writing…</p> : null}
            <SourceList sources={result.sources} />
            <Disclaimer text={result.disclaimer} />
          </Card>
          <Card>
            <h2 className="font-semibold">Possible concerns</h2>
            <div className="mt-3"><BulletList items={result.possible_concerns} /></div>
          </Card>
          <Card><h2 className="font-semibold">Suggested next steps</h2><div className="mt-3"><BulletList items={result.suggested_next_steps} /></div></Card>
          <Card><h2 className="font-semibold">Risk notes</h2><div className="mt-3"><BulletList items={result.risk_notes} /></div></Card>
        </div>
      )}
      <div className="mt-4 flex flex-wrap gap-3">
        <Button variant="primary" onClick={() => navigate("/twin")}>Open Dr. Vimlesh Pandey Twin Consultation</Button>
        <Button onClick={() => { setGeneric(null); setMeta(null); setRun((n) => n + 1); }}>Regenerate</Button>
      </div>
    </div>
  );
}
