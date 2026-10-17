import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { streamConsult } from "../lib/api";
import { useAppStore } from "../store/useAppStore";
import type { TwinResult } from "../types";
import { RichText } from "../components/RichText";
import { BulletList, Button, Card, Confidence, Disclaimer, Fold, PageHeader, Skeleton, SourceList } from "../components/ui";

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
      <PageHeader eyebrow="Doctor's Twin" title="The consultation" caption="The answer is first. Open a section when you want the cases, the plan, or the confidence number." />
      {!result && loading && <Skeleton className="h-48" />}
      {result && (
        <div className="space-y-3">
          <Card>
            <div className="mb-4 flex items-center gap-3">
              <img src="/doctor_photo.jpg?v=3" alt="Dr. Vimlesh Pandey" className="h-12 w-12 rounded-full object-cover object-top" />
              <p className="text-sm text-[#5c6b7a] dark:text-[#b7c0c7]">Dr. Vimlesh Pandey’s twin</p>
            </div>
            {result.assessment ? <RichText text={result.assessment} /> : loading ? <p className="mt-3 text-sm">Writing…</p> : null}
            <Disclaimer text={result.disclaimer} />
          </Card>
          {!!result.clarifying_questions?.length && (
            <Fold title="Still to clarify">
              <BulletList items={result.clarifying_questions} />
            </Fold>
          )}
          <Fold title="Past cases used">
            <ul className="space-y-2 text-sm">
              {result.historical_patterns?.map((item) => (
                <li key={String(item.case_id)}>Case {item.case_id}: {item.diagnosis} ({Number(item.final_match_score ?? item.match_score ?? 0).toFixed(2)})</li>
              ))}
            </ul>
            <SourceList sources={result.sources} />
          </Fold>
          <Fold title="Tests, actions, and follow-up">
            <div className="grid gap-4 md:grid-cols-3">
              <div><h3 className="font-semibold">Tests</h3><BulletList items={result.recommended_tests} /></div>
              <div><h3 className="font-semibold">Actions</h3><BulletList items={result.immediate_actions} /></div>
              <div><h3 className="font-semibold">Follow-up</h3><BulletList items={result.follow_up_plan} /></div>
            </div>
          </Fold>
          <Fold title="Confidence">
            <Confidence result={result} />
          </Fold>
        </div>
      )}
      <div className="mt-4 flex flex-wrap gap-3">
        <Button variant="primary" onClick={() => navigate("/compare")}>See them side by side</Button>
        <Button onClick={() => { setTwin(null); setMeta(null); setRun((n) => n + 1); }}>Regenerate</Button>
        <Link className="self-center text-sm underline" to="/studio">All comparison pages</Link>
      </div>
    </div>
  );
}
