import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Copy, RefreshCw } from "lucide-react";
import { toast } from "sonner";
import { PatientForm } from "../components/PatientForm";
import { RichText } from "../components/RichText";
import { BulletList, Button, Card, Disclaimer, Fold, PageHeader } from "../components/ui";
import { streamConsult } from "../lib/api";
import { bmiOf } from "../lib/utils";
import { useAppStore } from "../store/useAppStore";
import { demoPatient, type ChatMessage, type GenericResult, type TwinResult } from "../types";

export default function ConsultationPortal() {
  const navigate = useNavigate();
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
  const [comeInNote, setComeInNote] = useState("");

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

  useEffect(() => {
    if (portal.view === "Doctor") setEdited(portal.draft || "");
  }, [portal.view, portal.draft]);

  const status = portal.doctorStatus;
  return (
    <div>
      <PageHeader eyebrow="Consultation" title={portal.patient ? portal.patient.name : "Your consultation"} caption="The Doctor's Twin answers from the details you just gave. Open a section only if you want it." />
      {portal.view === "Doctor" ? (
        <Card>
          <h2 className="text-xl font-semibold">Doctor's view</h2>
          <p className="mt-1 text-sm text-[#3d5270] dark:text-[#c9d7ea]">The consultation is shown as the patient sees it. Edit the draft underneath if you want to change it.</p>
          {!portal.patient || !portal.draft ? (
            <p className="mt-4 text-sm">Start the consultation from the patient view first.</p>
          ) : (
            <div className="mt-4 space-y-4">
              <p className="text-sm">{portal.patient.name} · age {portal.patient.age} · BMI {bmiOf(portal.patient)} · LDL {portal.patient.ldl}</p>
              <div className="rounded-2xl bg-[#f3f7fc] p-4 dark:bg-[#071422]">
                <RichText text={edited || portal.draft} />
              </div>
              <label className="block text-sm">Change the consultation
                <textarea className="mt-1 min-h-48 w-full rounded-xl border border-[#c5d7ea] bg-white p-3 text-sm text-[#0b1f3a] dark:border-white/10 dark:bg-[#071422] dark:text-[#e7f0fa]" value={edited} onChange={(e) => setEdited(e.target.value)} />
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
                <Button onClick={() => {
                  const reason = comeInNote.trim();
                  const content = reason
                    ? `Please come in person. Dr. Pandey wants to see you at the clinic. ${reason}`
                    : "Please come in person. Dr. Pandey wants to see you at the clinic. This is something the twin should not explain on its own.";
                  patch({ doctorStatus: "in_person", chat: [...portal.chat, { role: "assistant", content }], view: "Patient" });
                  toast.success("The patient has been asked to come in.");
                }}>Ask them to come in</Button>
              </div>
              <label className="block text-sm text-[#0b1f3a] dark:text-[#e7f0fa]">If this should be said in person
                <textarea className="mt-1 min-h-24 w-full rounded-xl border border-[#c5d7ea] bg-white p-3 text-sm text-[#0b1f3a] placeholder:text-[#5c7190] dark:border-white/10 dark:bg-[#071422] dark:text-[#e7f0fa] dark:placeholder:text-[#9eb0c8]" placeholder="For example: this looks serious, and the twin should not be the one to explain it." value={comeInNote} onChange={(e) => setComeInNote(e.target.value)} />
              </label>
              <p className="text-sm text-[#3d5270] dark:text-[#c9d7ea]">Use this when the case is serious and the twin cannot say it properly. The patient is asked to see Dr. Pandey in person.</p>
              <Disclaimer text="This review is a demo. A real clinic needs access control and an audit log." />
            </div>
          )}
        </Card>
      ) : !portal.patient && (
        <Card>
          <h2 className="font-display text-2xl">Your details</h2>
          <div className="mt-4">
            <PatientForm initial={demoPatient} mode="portal" submitLabel="Continue" onSubmit={(patient) => { saveIntake(patient); toast.success("Details saved."); }} />
          </div>
        </Card>
      )}
      {portal.view !== "Doctor" && portal.patient && portal.chat.length === 0 && !draftText && (
        <Card>
          <p className="text-sm text-[#5c6b7a] dark:text-[#b7c0c7]">Age {portal.patient.age} · BP {portal.patient.bp || "not given"} · LDL {portal.patient.ldl}</p>
          <Button className="mt-5" variant="primary" disabled={busy} onClick={() => begin("specialist")}>{busy ? "Writing…" : "Start the consultation"}</Button>
        </Card>
      )}
      {portal.view !== "Doctor" && (portal.chat.length > 0 || draftText) && (
        <Card>
          {status === "approved" && <p className="mb-3 rounded-xl bg-[#e7f1fb] px-4 py-3 text-sm text-[#0b1f3a] dark:bg-[#16345c] dark:text-white">A clinician approved this consultation.</p>}
          {status === "edited_approved" && <p className="mb-3 rounded-xl bg-[#e7f1fb] px-4 py-3 text-sm text-[#0b1f3a] dark:bg-[#16345c] dark:text-white">A clinician edited and approved this consultation.</p>}
          {status === "rejected" && <p className="mb-3 rounded-xl bg-amber-100 px-4 py-3 text-sm text-amber-950 dark:bg-amber-950/40 dark:text-amber-50">A clinician rejected this draft. Please arrange a direct review.</p>}
          {status === "in_person" && <p className="mb-3 rounded-xl bg-[#e7f1fb] px-4 py-3 text-sm font-semibold text-[#0b1f3a] dark:bg-[#16345c] dark:text-white">Dr. Pandey wants to see you in person. This is something the twin should not explain on its own. Please come to the clinic.</p>}
          <div className="max-h-[540px] space-y-3 overflow-y-auto pr-1">
            {portal.chat.map((message, index) => (
              <div key={`${message.role}-${index}`} className={`w-fit max-w-[75%] rounded-2xl px-3 py-2 text-sm leading-6 ${message.role === "user" ? "ml-auto bg-[#123a6b] text-white" : "bg-[#f3f7fc] dark:bg-[#071422]"}`}>
                {message.role === "assistant" ? <RichText text={message.content} className="" /> : <p className="whitespace-pre-wrap">{message.content}</p>}
                {message.role === "assistant" && (
                  <div className="mt-2 flex gap-2">
                    <button aria-label="Copy message" onClick={() => copy(message.content)}><Copy size={14} /></button>
                    <button aria-label="Regenerate message" onClick={() => regenerate(index)}><RefreshCw size={14} /></button>
                  </div>
                )}
              </div>
            ))}
            {draftText && <div className="w-fit max-w-[75%] rounded-2xl bg-[#f3f7fc] px-3 py-2 text-sm leading-6 dark:bg-[#071422]"><RichText text={draftText} streaming className="" /></div>}
          </div>
          <form className="mt-4 flex items-center gap-2" onSubmit={(event) => { event.preventDefault(); if (!question.trim() || busy) return; const text = question.trim(); setQuestion(""); ask(text, portal.chat); }}>
            <input className="h-10 min-w-0 flex-1 rounded-full border border-[#c5d7ea] bg-white px-4 text-sm text-[#0b1f3a] placeholder:text-[#5c7190] dark:border-white/10 dark:bg-[#071422] dark:text-[#e7f0fa] dark:placeholder:text-[#9eb0c8]" placeholder="Ask a follow-up" value={question} onChange={(e) => setQuestion(e.target.value)} />
            <Button className="h-10 shrink-0 rounded-full px-4" variant="primary" disabled={busy}>{busy ? "…" : "Send"}</Button>
          </form>
        </Card>
      )}
      {portal.view !== "Doctor" && portal.patient && (
        <div className="mt-4 space-y-3">
          <Fold title="Change these details">
            <PatientForm initial={portal.patient} mode="portal" submitLabel="Save" onSubmit={(patient) => { saveIntake(patient); toast.success("Details saved."); }} />
          </Fold>
          {portal.twin && (
            <>
              <Fold title="Tests, actions, and follow-up">
                <div className="grid gap-4 md:grid-cols-3">
                  <div><h3 className="font-semibold">Tests</h3><BulletList items={portal.twin.recommended_tests} /></div>
                  <div><h3 className="font-semibold">Actions</h3><BulletList items={portal.twin.immediate_actions} /></div>
                  <div><h3 className="font-semibold">Follow-up</h3><BulletList items={portal.twin.follow_up_plan} /></div>
                </div>
              </Fold>
              <Fold title="Why this reading">
                <p className="text-sm leading-6 text-[#0b1f3a] dark:text-[#e7f0fa]">This follows visits Dr. Pandey has already seen. They are similar histories, not a copy of this patient, and they are why the reading takes this direction.</p>
                <ul className="mt-3 space-y-2 text-sm text-[#0b1f3a] dark:text-[#e7f0fa]">
                  {(portal.twin.historical_patterns || []).map((item) => (
                    <li key={String(item.case_id)}>Case {item.case_id}: {item.diagnosis}</li>
                  ))}
                </ul>
                <div className="mt-4 flex flex-wrap gap-2">
                  <Button variant="primary" onClick={() => navigate("/graph?scope=patient&from=consultation")}>This patient's graph</Button>
                  <Button onClick={() => navigate("/graph?scope=all&from=consultation")}>Entire graph</Button>
                </div>
              </Fold>
            </>
          )}
          <button className="text-sm text-[#123a6b] underline dark:text-[#8eb8e8]" onClick={() => { reset(); setDraftText(""); toast.success("Consultation cleared."); }}>Start again</button>
        </div>
      )}
    </div>
  );
}
