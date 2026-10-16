import { useState } from "react";
import { Copy, RefreshCw } from "lucide-react";
import { toast } from "sonner";
import { PatientForm } from "../components/PatientForm";
import { BulletList, Button, Card, Disclaimer, Note, PageHeader } from "../components/ui";
import { streamConsult } from "../lib/api";
import { bmiOf } from "../lib/utils";
import { useAppStore } from "../store/useAppStore";
import { demoPatient, type ChatMessage, type GenericResult, type TwinResult } from "../types";

export default function ConsultationPortal() {
  const portal = useAppStore((s) => s.portal);
  const saveIntake = useAppStore((s) => s.savePortalIntake);
  const patch = useAppStore((s) => s.patchPortal);
  const reset = useAppStore((s) => s.resetPortalChat);
  const setGeneric = useAppStore((s) => s.setGenericResult);
  const setTwin = useAppStore((s) => s.setTwinResult);
  const [busy, setBusy] = useState(false);
  const [draftText, setDraftText] = useState("");
  const [edited, setEdited] = useState(portal.draft || "");
  const [question, setQuestion] = useState("");

  async function begin(mode: "general" | "specialist") {
    if (!portal.patient) return;
    setBusy(true);
    setDraftText("");
    let meta: TwinResult | null = null;
    let acc = "";
    try {
      await streamConsult({ kind: mode === "general" ? "generic" : "twin", patient: portal.patient }, (event) => {
        if (event.type === "meta" && event.result) meta = event.result as TwinResult;
        if (event.type === "token" && event.text) {
          acc += event.text;
          setDraftText(acc);
        }
        if (event.type === "done") {
          const text = event.text || acc;
          const twin = mode === "specialist" && meta ? { ...meta, assessment: text } : null;
          patch({
            mode,
            chat: [{ role: "assistant", content: text, sources: meta?.sources }],
            draft: text,
            originalDraft: text,
            twin,
            doctorStatus: null,
            approved: null,
            rejected: false,
            view: "Patient",
          });
          setEdited(text);
          setDraftText("");
          if (mode === "general" && meta) setGeneric({ ...(meta as unknown as GenericResult), consultation_summary: text });
          if (twin) setTwin(twin);
        }
      });
      toast.success(mode === "general" ? "General consultation started." : "Specialist consultation started.");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Consultation failed.");
    } finally {
      setBusy(false);
    }
  }

  async function ask(text: string, history: ChatMessage[]) {
    if (!portal.patient || !portal.mode) return;
    setBusy(true);
    setDraftText("");
    let acc = "";
    const prior = [...history, { role: "user" as const, content: text }];
    patch({ chat: prior });
    try {
      await streamConsult({
        kind: "followup",
        mode: portal.mode,
        patient: portal.patient,
        user_question: text,
        twin: portal.twin,
        history,
      }, (event) => {
        if (event.type === "token" && event.text) {
          acc += event.text;
          setDraftText(acc);
        }
        if (event.type === "done") {
          patch({ chat: [...prior, { role: "assistant", content: event.text || acc, sources: (event.sources as ChatMessage["sources"]) || [] }] });
          setDraftText("");
        }
      });
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "The reply failed.");
    } finally {
      setBusy(false);
    }
  }

  function copy(text: string) {
    navigator.clipboard.writeText(text).then(() => toast.success("Copied.")).catch(() => toast.error("Could not copy."));
  }

  function regenerate(index: number) {
    const prior = portal.chat.slice(0, index);
    const lastUser = [...prior].reverse().find((message) => message.role === "user");
    if (!lastUser || !portal.mode) {
      begin(portal.mode || "general");
      return;
    }
    const history = prior.slice(0, prior.map((message) => message.role).lastIndexOf("user"));
    patch({ chat: history });
    ask(lastUser.content, history);
  }

  const status = portal.doctorStatus;
  return (
    <div>
      <PageHeader eyebrow="Portal" title="Consultation Portal" caption="One-on-one consultation with guided intake, live chat, and a clinician review step." />
      <Note title="How this works">Fill the guided intake, choose General AI or the Specialist Twin, then continue in chat. A clinician can accept, reject, or edit the draft before it is shared back.</Note>
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        {portal.mode === "specialist" ? (
          <div className="flex rounded-full border border-slate-300 p-1 text-sm dark:border-white/15">
            {(["Patient", "Doctor"] as const).map((view) => (
              <button key={view} className={`rounded-full px-3 py-1 ${portal.view === view ? "bg-sky-500 text-slate-950" : ""}`} onClick={() => { setEdited(portal.draft || ""); patch({ view }); }}>{view}</button>
            ))}
          </div>
        ) : <span className="rounded-full border border-slate-300 px-3 py-1 text-sm dark:border-white/15">Patient view</span>}
        <p className="text-sm text-slate-500">Intake → consultation → chat → doctor review</p>
      </div>

      {portal.view === "Doctor" ? (
        <Card>
          <h2 className="text-xl font-semibold">Clinician review</h2>
          {portal.mode !== "specialist" ? (
            <div className="mt-3">
              <p>Doctor review is available only for the Dr. Vimlesh Pandey Specialist Twin.</p>
              <Button className="mt-3" variant="primary" onClick={() => patch({ view: "Patient" })}>Back to patient chat</Button>
            </div>
          ) : !portal.patient || !portal.draft ? (
            <p className="mt-3">Start a specialist consultation first.</p>
          ) : (
            <div className="mt-4 space-y-4">
              <div className="rounded-xl bg-slate-100 p-3 text-sm dark:bg-white/5">
                <p><strong>{portal.patient.name}</strong> · age {portal.patient.age} · BMI {bmiOf(portal.patient)}</p>
                <p>BP {portal.patient.bp} · LDL {portal.patient.ldl} · HbA1c {portal.patient.hba1c}</p>
              </div>
              <label className="block text-sm">Clinician-edited consultation draft
                <textarea className="mt-1 min-h-64 w-full rounded-xl border border-slate-300 bg-white p-3 text-sm dark:border-white/15 dark:bg-white/5" value={edited} onChange={(e) => setEdited(e.target.value)} />
              </label>
              <div className="flex flex-wrap gap-3">
                <Button variant="primary" onClick={() => {
                  const changed = edited.trim() !== (portal.originalDraft || "").trim();
                  const doctorStatus = changed ? "edited_approved" : "approved";
                  const note = changed ? `Doctor update: Edited and approved.\n\n${edited}` : "Doctor update: Approved without changes.";
                  patch({ approved: edited, rejected: false, doctorStatus, draft: edited, chat: [...portal.chat, { role: "assistant", content: note }], view: "Patient" });
                  toast.success(changed ? "Accepted with edits." : "Accepted.");
                }}>Accept</Button>
                <Button variant="danger" onClick={() => {
                  patch({ rejected: true, approved: null, doctorStatus: "rejected", chat: [...portal.chat, { role: "assistant", content: "Doctor update: Rejected. Please schedule a direct clinical review." }], view: "Patient" });
                  toast.success("Draft rejected.");
                }}>Reject</Button>
                <Button onClick={() => patch({ view: "Patient" })}>Back to patient chat</Button>
              </div>
              <Disclaimer text="This panel is a demo clinician workflow. A real deployment needs access control, audit logs, and role-based approval." />
            </div>
          )}
        </Card>
      ) : (
        <div className="space-y-4">
          <Card>
            <h2 className="text-xl font-semibold">Guided patient intake</h2>
            <div className="mt-4">
              <PatientForm initial={portal.patient || demoPatient} mode="portal" submitLabel="Save Intake" onSubmit={(patient) => { saveIntake(patient); toast.success("Intake saved. Choose a consultation type to begin."); }} />
            </div>
          </Card>
          <Card>
            <h2 className="text-xl font-semibold">Choose consultation type</h2>
            {!portal.patient && <p className="mt-3 text-sm">Save the intake first to start a consultation.</p>}
            {portal.patient && portal.chat.length > 0 && <p className="mt-3 text-sm">Active consultation: {portal.mode === "specialist" ? "Dr. Vimlesh Pandey Specialist Twin" : "General AI"}</p>}
            {portal.patient && portal.chat.length === 0 && (
              <div className="mt-4 grid gap-4 md:grid-cols-2">
                <div className="rounded-2xl border border-slate-200 p-4 dark:border-white/10">
                  <h3 className="font-semibold">General AI consultation</h3>
                  <p className="mt-1 text-sm text-slate-500">Broad guidance from the intake only. A baseline, without specialist case memory.</p>
                  <Button className="mt-3" variant="primary" disabled={busy} onClick={() => begin("general")}>Start General Consultation</Button>
                </div>
                <div className="rounded-2xl border border-slate-200 p-4 dark:border-white/10">
                  <h3 className="font-semibold">Dr. Vimlesh Pandey Specialist Twin</h3>
                  <p className="mt-1 text-sm text-slate-500">Specialist reasoning with historical cases and graph relationships.</p>
                  <Button className="mt-3" variant="primary" disabled={busy} onClick={() => begin("specialist")}>Start Specialist Consultation</Button>
                </div>
              </div>
            )}
          </Card>
          <Card>
            <div className="flex flex-wrap items-center justify-between gap-3">
              <h2 className="text-xl font-semibold">Consultation chat</h2>
              {portal.chat.length > 0 && (
                <div className="flex gap-2">
                  <Button disabled={portal.mode !== "specialist"} onClick={() => { setEdited(portal.draft || ""); patch({ view: "Doctor" }); }}>Open Doctor Review</Button>
                  <Button onClick={() => { reset(); setDraftText(""); toast.success("Reset done."); }}>Reset consultation</Button>
                </div>
              )}
            </div>
            {status === "approved" && <p className="mt-3 rounded-xl bg-emerald-500/10 px-3 py-2 text-sm text-emerald-800 dark:text-emerald-100">Doctor has reviewed and approved the consultation.</p>}
            {status === "edited_approved" && <p className="mt-3 rounded-xl bg-emerald-500/10 px-3 py-2 text-sm text-emerald-800 dark:text-emerald-100">Doctor has edited and approved the consultation.</p>}
            {status === "rejected" && <p className="mt-3 rounded-xl bg-amber-500/10 px-3 py-2 text-sm text-amber-900 dark:text-amber-100">Doctor has rejected this draft. Please schedule a direct clinical review.</p>}
            {portal.chat.length === 0 && !draftText && <p className="mt-3 text-sm text-slate-500">Start a consultation to enable chat.</p>}
            <div className="mt-4 max-h-[540px] space-y-3 overflow-y-auto pr-1">
              {portal.chat.map((message, index) => (
                <div key={`${message.role}-${index}`} className={`max-w-[92%] rounded-2xl px-4 py-3 text-sm leading-6 ${message.role === "user" ? "ml-auto bg-sky-500 text-slate-950" : "bg-slate-100 dark:bg-white/5"}`}>
                  <p className="whitespace-pre-wrap">{message.content}</p>
                  {message.role === "assistant" && (
                    <div className="mt-2 flex gap-2">
                      <button aria-label="Copy message" onClick={() => copy(message.content)}><Copy size={14} /></button>
                      <button aria-label="Regenerate message" onClick={() => regenerate(index)}><RefreshCw size={14} /></button>
                    </div>
                  )}
                </div>
              ))}
              {draftText && <div className="max-w-[92%] rounded-2xl bg-slate-100 px-4 py-3 text-sm leading-6 dark:bg-white/5"><p className="whitespace-pre-wrap">{draftText}<span className="ml-1 inline-block h-3 w-1 animate-pulse bg-sky-500" /></p></div>}
            </div>
            {portal.mode === "specialist" && portal.twin && (
              <div className="mt-4 grid gap-3 md:grid-cols-3">
                <Card><h3 className="font-semibold">Immediate actions</h3><BulletList items={portal.twin.immediate_actions} /></Card>
                <Card><h3 className="font-semibold">Recommended tests</h3><BulletList items={portal.twin.recommended_tests} /></Card>
                <Card><h3 className="font-semibold">Follow-up plan</h3><BulletList items={portal.twin.follow_up_plan} /></Card>
              </div>
            )}
            {portal.chat.length > 0 && (
              <form className="mt-4 flex gap-2" onSubmit={(event) => { event.preventDefault(); if (!question.trim() || busy) return; const text = question.trim(); setQuestion(""); ask(text, portal.chat); }}>
                <input className="flex-1 rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm dark:border-white/15 dark:bg-white/5" placeholder="Ask a follow-up question" value={question} onChange={(e) => setQuestion(e.target.value)} />
                <Button variant="primary" disabled={busy}>{busy ? "Thinking…" : "Send"}</Button>
              </form>
            )}
          </Card>
        </div>
      )}
    </div>
  );
}
