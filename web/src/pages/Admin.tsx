import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { toast } from "sonner";
import { DataTable } from "../components/DataTable";
import { Button, Card, Note, PageHeader, Skeleton } from "../components/ui";
import { getJson } from "../lib/api";
import { useAppStore } from "../store/useAppStore";
import { analysisDefaults, type Patient } from "../types";

const colors = ["#0ea5e9", "#14b8a6", "#6366f1", "#f59e0b"];

interface RegistryRow { title: string; filename: string; description: string; exists: boolean; rows: number }
interface Profile extends Record<string, unknown> { patient_id?: string; age?: number; sex?: string; chief_complaint?: string; history?: string; medications?: string; ldl?: number; hba1c?: number }

export default function Admin() {
  const navigate = useNavigate();
  const setPatient = useAppStore((s) => s.setPatient);
  const [stats, setStats] = useState<Record<string, number> | null>(null);
  const [registry, setRegistry] = useState<RegistryRow[]>([]);
  const [patients, setPatients] = useState<Profile[]>([]);
  const [cases, setCases] = useState<Record<string, unknown>[]>([]);

  useEffect(() => {
    Promise.all([
      getJson<{ stats: Record<string, number>; registry: RegistryRow[] }>("/api/datasets"),
      getJson<{ patients: Profile[] }>("/api/patients"),
      getJson<{ cases: Record<string, unknown>[] }>("/api/cases/catalog"),
    ]).then(([data, people, catalog]) => {
      setStats(data.stats);
      setRegistry(data.registry);
      setPatients(people.patients);
      setCases(catalog.cases);
    }).catch((error: Error) => toast.error(error.message));
  }, []);

  const pie = stats ? [
    { name: "Doctor cases", value: stats.doctor_cases },
    { name: "Patient profiles", value: stats.patient_profiles },
    { name: "Graph nodes", value: stats.graph_nodes },
    { name: "Graph edges", value: stats.graph_edges },
  ] : [];

  function loadProfile(row: Profile) {
    const sex = String(row.sex || "").toUpperCase();
    const patient: Patient = {
      ...analysisDefaults,
      name: `Profile ${row.patient_id}`,
      age: Number(row.age) || analysisDefaults.age,
      gender: sex.startsWith("M") ? "Male" : sex.startsWith("F") ? "Female" : "Other",
      symptoms: String(row.chief_complaint || analysisDefaults.symptoms),
      medical_history: String(row.history || ""),
      current_medications: String(row.medications || ""),
      ldl: Number(row.ldl) || 0,
      hba1c: Number(row.hba1c) || 0,
      profile_id: String(row.patient_id || ""),
    };
    setPatient(patient);
    toast.success(`Loaded profile ${row.patient_id}. Height and weight stay as defaults because the profile file does not store them.`);
    navigate("/patient");
  }

  return (
    <div className="space-y-4">
      <PageHeader eyebrow="Admin" title="Admin / Dataset" caption="Operational view of the CardioTwin data assets." />
      <Note title="Patient Analysis clarification">Patient Analysis is the live input for the current session. It is not automatically a pre-existing Dr. Pandey record. Loading a profile below attaches that id so later prompts can include its timeline.</Note>
      {!stats && <Skeleton className="h-40" />}
      {stats && (
        <>
          <div className="grid gap-3 md:grid-cols-4">
            {pie.map((item) => <Card key={item.name}><p className="text-sm text-slate-500">{item.name}</p><p className="text-3xl font-semibold">{item.value}</p></Card>)}
          </div>
          <Card className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pie} dataKey="value" nameKey="name" innerRadius={70} outerRadius={110}>
                  {pie.map((item, index) => <Cell key={item.name} fill={colors[index % colors.length]} />)}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </>
      )}
      <Card><p className="text-sm text-emerald-700 dark:text-emerald-200">CardioTwin AI dataset pipeline is active and ready for expansion.</p></Card>
      <Card>
        <h2 className="mb-3 font-semibold">Dataset registry</h2>
        <div className="space-y-3">
          {registry.map((item) => (
            <div key={item.filename} className="grid gap-1 border-b border-slate-200 pb-3 last:border-0 dark:border-white/10 md:grid-cols-[180px_1fr_120px]">
              <p className="font-semibold">{item.title}</p>
              <p className="text-sm text-slate-500">{item.description}</p>
              <p className="text-sm">{item.exists ? `${item.rows} rows` : "Missing"}</p>
            </div>
          ))}
        </div>
      </Card>
      <Card>
        <h2 className="mb-3 font-semibold">Patient profiles</h2>
        <DataTable
          rows={patients}
          searchKeys={["patient_id", "chief_complaint", "history", "medications", "sex"]}
          filterKey="sex"
          columns={[
            { key: "patient_id", label: "ID" },
            { key: "age", label: "Age" },
            { key: "sex", label: "Sex" },
            { key: "chief_complaint", label: "Complaint" },
            { key: "ldl", label: "LDL" },
            { key: "hba1c", label: "HbA1c" },
            { key: "load", label: "Use", render: (row) => <Button onClick={() => loadProfile(row as Profile)}>Load</Button> },
          ]}
        />
      </Card>
      <Card>
        <h2 className="mb-3 font-semibold">Historical case catalog</h2>
        <DataTable
          rows={cases}
          searchKeys={["case_id", "symptoms", "diagnosis", "treatment_decision", "outcome"]}
          filterKey="diagnosis"
          columns={[
            { key: "case_id", label: "Case" },
            { key: "age", label: "Age" },
            { key: "sex", label: "Sex" },
            { key: "diagnosis", label: "Diagnosis" },
            { key: "treatment_decision", label: "Decision" },
            { key: "outcome", label: "Outcome" },
          ]}
        />
      </Card>
    </div>
  );
}
