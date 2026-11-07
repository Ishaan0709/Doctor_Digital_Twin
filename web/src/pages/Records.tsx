import { useEffect, useState } from "react";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Card, PageHeader, Skeleton } from "../components/ui";
import { getJson } from "../lib/api";

interface Profile {
  patient_id: string;
  age?: number | string;
  sex?: string;
  chief_complaint?: string;
  history?: string;
  medications?: string;
  ldl?: number | string;
  hba1c?: number | string;
}

interface Visit {
  date?: string;
  systolic_bp?: number | string;
  diastolic_bp?: number | string;
  hba1c?: number | string;
  weight_kg?: number | string;
}

function num(value: number | string | undefined) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

export default function Records() {
  const [patients, setPatients] = useState<Profile[] | null>(null);
  const [selected, setSelected] = useState<string>("");
  const [visits, setVisits] = useState<Visit[] | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    getJson<{ patients: Profile[] }>("/api/patients")
      .then((data) => {
        setPatients(data.patients);
        if (data.patients[0]) setSelected(String(data.patients[0].patient_id));
      })
      .catch(() => setFailed(true));
  }, []);

  useEffect(() => {
    if (!selected) return;
    setVisits(null);
    getJson<{ timeline: Visit[] }>(`/api/patients/${selected}/timeline`)
      .then((data) => setVisits(data.timeline))
      .catch(() => setVisits([]));
  }, [selected]);

  const chart = (visits || [])
    .map((visit) => ({
      date: String(visit.date || ""),
      systolic: num(visit.systolic_bp),
      hba1c: num(visit.hba1c),
    }))
    .filter((row) => row.date);

  const current = patients?.find((item) => String(item.patient_id) === selected);

  return (
    <div>
      <PageHeader eyebrow="Records" title="Recorded measurements" caption="These rows come from the saved profile and timeline tables. They are not a new diagnosis." />
      {failed && <Card>The record list could not be loaded.</Card>}
      {!patients && !failed && <Skeleton className="h-40" />}
      {patients && (
        <div className="grid gap-4 lg:grid-cols-[280px_1fr]">
          <Card className="max-h-[32rem] overflow-auto">
            <h2 className="text-sm font-semibold">Profiles</h2>
            <ul className="mt-3 space-y-1">
              {patients.slice(0, 40).map((patient) => (
                <li key={patient.patient_id}>
                  <button
                    className={`w-full rounded-xl px-3 py-2 text-left text-sm transition hover:bg-[#e7f1fb] dark:hover:bg-white/5 ${selected === String(patient.patient_id) ? "bg-[#123a6b] text-white" : ""}`}
                    onClick={() => setSelected(String(patient.patient_id))}
                  >
                    <span className="block font-semibold">{patient.patient_id}</span>
                    <span className="block text-xs opacity-80">{patient.chief_complaint}</span>
                  </button>
                </li>
              ))}
            </ul>
          </Card>
          <div className="space-y-4">
            {current && (
              <Card>
                <p className="text-xs font-semibold uppercase tracking-[0.14em] text-[#123a6b] dark:text-[#8eb8e8]">Recorded profile</p>
                <h2 className="mt-1 text-2xl font-semibold">{current.patient_id}</h2>
                <p className="mt-2 text-sm leading-6 text-[#2c4060] dark:text-[#d5e4f0]">
                  {current.age} · {current.sex}. {current.chief_complaint}. History: {current.history || "not recorded"}. Medicines: {current.medications || "not recorded"}.
                </p>
                <p className="mt-2 text-sm">LDL {current.ldl ?? "—"} · HbA1c {current.hba1c ?? "—"}</p>
              </Card>
            )}
            <Card>
              <h2 className="text-base font-semibold">Blood pressure and HbA1c over the recorded dates</h2>
              <p className="mt-1 text-sm text-[#2c4060] dark:text-[#d5e4f0]">The line is the saved measurement. It is not a doctor’s interpretation of the trend.</p>
              {!visits && <Skeleton className="mt-4 h-56" />}
              {visits && chart.length === 0 && <p className="mt-4 text-sm">No dated measurements for this profile.</p>}
              {chart.length > 0 && (
                <div className="mt-4 h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chart}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#94a3b833" />
                      <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                      <YAxis tick={{ fontSize: 11 }} />
                      <Tooltip />
                      <Line type="monotone" dataKey="systolic" name="Systolic BP" stroke="#123a6b" strokeWidth={2} dot={false} />
                      <Line type="monotone" dataKey="hba1c" name="HbA1c" stroke="#0f766e" strokeWidth={2} dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}
            </Card>
          </div>
        </div>
      )}
    </div>
  );
}
