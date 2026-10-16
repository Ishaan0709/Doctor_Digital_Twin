import { useState } from "react";
import type { Patient } from "../types";
import { demoPatient } from "../types";
import { Button, fieldClass } from "./ui";

const durations = ["1-2 days", "1 week", "2 weeks", "1 month", "3 months", "6+ months"];
const patterns = [
  "Chest pain / pressure on exertion",
  "Breathlessness on exertion",
  "Palpitations / irregular heartbeat",
  "Fatigue / reduced exercise tolerance",
  "Atypical discomfort (jaw/back/epigastric)",
  "No symptoms (preventive check)",
];
const risks = ["Diabetes", "Hypertension", "Smoking", "Family history of early CAD", "Obesity", "High stress", "High cholesterol", "CKD"];

export function PatientForm({
  initial,
  mode,
  submitLabel,
  onSubmit,
}: {
  initial: Patient;
  mode: "portal" | "analysis";
  submitLabel: string;
  onSubmit: (patient: Patient) => void;
}) {
  const [form, setForm] = useState<Patient>(initial);
  const [pattern, setPattern] = useState(patterns[0]);
  const [details, setDetails] = useState("Exertional chest pain radiating to left arm, improves with rest.");
  const [selected, setSelected] = useState<string[]>(["Diabetes", "Hypertension", "Smoking", "Family history of early CAD", "High cholesterol"]);

  function set<K extends keyof Patient>(key: K, value: Patient[K]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  function submit(event: React.FormEvent) {
    event.preventDefault();
    if (mode === "portal") {
      onSubmit({
        ...form,
        symptoms: `${pattern}. ${details}`.trim(),
        medical_history: `${form.medical_history}\nRisk factors selected: ${selected.join(", ")}`.trim(),
      });
      return;
    }
    onSubmit(form);
  }

  return (
    <form onSubmit={submit} className="space-y-4">
      <div className="grid gap-4 md:grid-cols-3">
        <label className="text-sm">Patient name
          <input required className={`${fieldClass} mt-1`} value={form.name} onChange={(e) => set("name", e.target.value)} />
        </label>
        <label className="text-sm">Age
          <input required type="number" min={1} max={120} className={`${fieldClass} mt-1`} value={form.age} onChange={(e) => set("age", Number(e.target.value))} />
        </label>
        <label className="text-sm">Gender
          <select className={`${fieldClass} mt-1`} value={form.gender} onChange={(e) => set("gender", e.target.value)}>
            {["Male", "Female", "Other"].map((option) => <option key={option}>{option}</option>)}
          </select>
        </label>
        <label className="text-sm">Height (cm)
          <input required type="number" min={50} max={250} step="0.1" className={`${fieldClass} mt-1`} value={form.height_cm} onChange={(e) => set("height_cm", Number(e.target.value))} />
        </label>
        <label className="text-sm">Weight (kg)
          <input required type="number" min={20} max={300} step="0.1" className={`${fieldClass} mt-1`} value={form.weight_kg} onChange={(e) => set("weight_kg", Number(e.target.value))} />
        </label>
        <label className="text-sm">Duration
          {mode === "portal" ? (
            <select className={`${fieldClass} mt-1`} value={form.symptom_duration} onChange={(e) => set("symptom_duration", e.target.value)}>
              {durations.map((option) => <option key={option}>{option}</option>)}
            </select>
          ) : (
            <input className={`${fieldClass} mt-1`} value={form.symptom_duration} onChange={(e) => set("symptom_duration", e.target.value)} />
          )}
        </label>
        <label className="text-sm">BP
          <input className={`${fieldClass} mt-1`} value={form.bp} onChange={(e) => set("bp", e.target.value)} placeholder="130/85" />
        </label>
        <label className="text-sm">LDL
          <input required type="number" min={0} max={400} step="0.1" className={`${fieldClass} mt-1`} value={form.ldl} onChange={(e) => set("ldl", Number(e.target.value))} />
        </label>
        <label className="text-sm">HbA1c
          <input required type="number" min={0} max={20} step="0.1" className={`${fieldClass} mt-1`} value={form.hba1c} onChange={(e) => set("hba1c", Number(e.target.value))} />
        </label>
      </div>
      {mode === "portal" ? (
        <>
          <label className="block text-sm">Main symptom pattern
            <select className={`${fieldClass} mt-1`} value={pattern} onChange={(e) => setPattern(e.target.value)}>
              {patterns.map((option) => <option key={option}>{option}</option>)}
            </select>
          </label>
          <label className="block text-sm">Symptom details
            <textarea className={`${fieldClass} mt-1 min-h-24`} value={details} onChange={(e) => setDetails(e.target.value)} />
          </label>
          <fieldset>
            <legend className="text-sm">Risk factors</legend>
            <div className="mt-2 grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
              {risks.map((risk) => (
                <label key={risk} className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={selected.includes(risk)}
                    onChange={(e) => setSelected((current) => e.target.checked ? [...current, risk] : current.filter((item) => item !== risk))}
                  />
                  {risk}
                </label>
              ))}
            </div>
          </fieldset>
        </>
      ) : (
        <label className="block text-sm">Symptoms
          <textarea className={`${fieldClass} mt-1 min-h-24`} value={form.symptoms} onChange={(e) => set("symptoms", e.target.value)} />
        </label>
      )}
      {(["medical_history", "family_history", "lifestyle", "current_medications", "optional_notes"] as const).map((key) => (
        <label key={key} className="block text-sm capitalize">{key.replace(/_/g, " ")}
          <textarea className={`${fieldClass} mt-1 min-h-20`} value={form[key]} onChange={(e) => set(key, e.target.value)} />
        </label>
      ))}
      <div className="flex flex-wrap gap-3">
        <Button type="submit" variant="primary">{submitLabel}</Button>
        <Button type="button" onClick={() => { setForm(mode === "portal" ? demoPatient : { ...demoPatient, symptoms: "Exertional chest discomfort, fatigue" }); }}>
          Use demo patient
        </Button>
      </div>
    </form>
  );
}
