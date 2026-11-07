import { useEffect, useMemo, useState } from "react";
import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Card, PageHeader, Skeleton } from "../components/ui";
import { getJson } from "../lib/api";

interface DatasetFile {
  title: string;
  filename: string;
  description: string;
  rows: number;
  columns: string[];
}

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

interface CaseRow {
  case_id?: string | number;
  age?: number | string;
  sex?: string;
  symptoms?: string;
  risk_factors?: string;
  tests?: string;
  diagnosis?: string;
  treatment_decision?: string;
  outcome?: string;
}

interface GraphNode {
  node_id?: string | number;
  name?: string;
  type?: string;
}

interface GraphEdge {
  source_id?: string | number;
  target_id?: string | number;
  source_name?: string;
  target_name?: string;
  relation?: string;
}

interface Tally {
  label: string;
  count: number;
}

interface Library {
  registry: DatasetFile[];
  style: Array<{ example_id?: string | number; style_rule?: string }>;
  nodes: GraphNode[];
  edges: GraphEdge[];
  diagnoses: Tally[];
  decisions: Tally[];
  profiles: Profile[];
  cases: CaseRow[];
}

const roles: Record<string, string> = {
  "doctor_cases_vimlesh_pandey.csv": "Retrieved as similar visits when the twin answers.",
  "patient_profiles.csv": "Saved cohort profiles. A live consultation is typed in separately.",
  "patient_timelines.csv": "Dated blood pressure, HbA1c, and weight for a chosen profile.",
  "graph_nodes.csv": "Named entities the graph walk can land on.",
  "graph_edges.csv": "The relation stored between two of those entities.",
  "doctor_style_examples.csv": "Tone rules placed in the twin prompt.",
};

function num(value: number | string | undefined) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function shown(value: number | string | undefined) {
  if (value === undefined || value === null || String(value).trim() === "") return "—";
  return String(value);
}

function Bars({ title, unit, rows }: { title: string; unit: string; rows: Tally[] }) {
  return (
    <Card className="min-h-[22rem]">
      <p className="text-xs uppercase tracking-[0.18em] text-[#8a6a3b]">{unit}</p>
      <h3 className="mt-1 font-display font-semibold text-3xl">{title}</h3>
      <div className="mt-4 h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={rows} layout="vertical" margin={{ top: 4, right: 16, left: 8, bottom: 4 }}>
            <CartesianGrid stroke="#eadfd2" horizontal={false} />
            <XAxis type="number" tick={{ fontSize: 12, fill: "#5c5348" }} allowDecimals={false} />
            <YAxis type="category" dataKey="label" width={168} tick={{ fontSize: 12, fill: "#172033" }} />
            <Tooltip cursor={{ fill: "rgba(184,149,106,0.12)" }} formatter={(value) => [`${value} cases`, "Count"]} />
            <Bar dataKey="count" fill="#172033" radius={[0, 8, 8, 0]} barSize={16} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}

function MeasureChart({
  title,
  unit,
  source,
  data,
  lines,
}: {
  title: string;
  unit: string;
  source: string;
  data: Array<Record<string, string | number | null>>;
  lines: Array<{ key: string; name: string; color: string }>;
}) {
  return (
    <Card>
      <p className="text-xs uppercase tracking-[0.18em] text-[#8a6a3b]">{unit}</p>
      <h3 className="mt-1 font-display font-semibold text-3xl">{title}</h3>
      <p className="mt-1 text-xs text-[#5c5348] dark:text-[#d9d0c5]">{source}</p>
      <div className="mt-4 h-72">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
            <CartesianGrid stroke="#eadfd2" />
            <XAxis dataKey="date" tick={{ fontSize: 11, fill: "#5c5348" }} />
            <YAxis tick={{ fontSize: 11, fill: "#5c5348" }} width={42} domain={["auto", "auto"]} />
            <Tooltip />
            {lines.map((line) => (
              <Line key={line.key} type="monotone" dataKey={line.key} name={line.name} stroke={line.color} strokeWidth={2.4} dot={{ r: 3 }} connectNulls={false} />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}

export default function Records() {
  const [library, setLibrary] = useState<Library | null>(null);
  const [failed, setFailed] = useState(false);
  const [selected, setSelected] = useState("");
  const [profileQuery, setProfileQuery] = useState("");
  const [caseQuery, setCaseQuery] = useState("");
  const [relation, setRelation] = useState("all");
  const [visits, setVisits] = useState<Visit[] | null>(null);

  useEffect(() => {
    getJson<Library>("/api/library")
      .then((data) => {
        setLibrary(data);
        if (data.profiles[0]) setSelected(String(data.profiles[0].patient_id));
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

  const profiles = useMemo(() => {
    const rows = library?.profiles || [];
    const query = profileQuery.trim().toLowerCase();
    if (!query) return rows;
    return rows.filter((row) =>
      `${row.patient_id} ${row.chief_complaint} ${row.history} ${row.sex}`.toLowerCase().includes(query),
    );
  }, [library, profileQuery]);

  const cases = useMemo(() => {
    const rows = library?.cases || [];
    const query = caseQuery.trim().toLowerCase();
    if (!query) return rows;
    return rows.filter((row) =>
      `${row.case_id} ${row.symptoms} ${row.diagnosis} ${row.treatment_decision} ${row.outcome} ${row.risk_factors}`.toLowerCase().includes(query),
    );
  }, [library, caseQuery]);

  const current = library?.profiles.find((item) => String(item.patient_id) === selected);
  const chart = (visits || []).map((visit) => ({
    date: String(visit.date || "").slice(0, 10),
    systolic: num(visit.systolic_bp),
    diastolic: num(visit.diastolic_bp),
    hba1c: num(visit.hba1c),
    weight: num(visit.weight_kg),
  }));
  const relations = ["all", ...Array.from(new Set((library?.edges || []).map((edge) => String(edge.relation || "")).filter(Boolean)))];
  const visibleEdges = (library?.edges || []).filter((edge) => relation === "all" || edge.relation === relation);
  const nodeGroups = useMemo(() => {
    const groups = new Map<string, GraphNode[]>();
    (library?.nodes || []).forEach((node) => {
      const type = String(node.type || "Unlabeled");
      groups.set(type, [...(groups.get(type) || []), node]);
    });
    return Array.from(groups.entries());
  }, [library]);

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Records"
        title="Six files. Every row is still in the file."
        caption="This is the store the twin reads. Cases are retrieved. The graph is walked. A timeline is attached only when that profile is chosen. None of these rows is a diagnosis."
      />
      {failed && <Card>The record library could not be loaded.</Card>}
      {!library && !failed && <Skeleton className="h-64" />}
      {library && (
        <>
          <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {library.registry.map((file) => (
              <Card key={file.filename} className="flex flex-col">
                <p className="text-xs uppercase tracking-[0.18em] text-[#8a6a3b]">{file.filename}</p>
                <div className="mt-3 flex items-end justify-between gap-3">
                  <h2 className="font-display font-semibold text-3xl leading-none">{file.title}</h2>
                  <p className="font-display font-semibold text-4xl leading-none text-[#172033] dark:text-[#f7f4ef]">{file.rows}</p>
                </div>
                <p className="mt-3 text-sm leading-6 text-[#5c5348] dark:text-[#d9d0c5]">{roles[file.filename] || file.description}</p>
                <div className="mt-4 flex flex-wrap gap-1.5">
                  {file.columns.map((column) => (
                    <span key={column} className="rounded-full bg-[#f4efe8] px-2.5 py-1 text-[11px] text-[#172033] dark:bg-white/10 dark:text-[#f4efe8]">
                      {column}
                    </span>
                  ))}
                </div>
              </Card>
            ))}
          </section>

          <section className="space-y-4">
            <div>
              <p className="text-xs uppercase tracking-[0.18em] text-[#8a6a3b]">doctor_cases_vimlesh_pandey.csv</p>
              <h2 className="mt-1 font-display font-semibold text-4xl">What Dr. Pandey recorded across {library.cases.length} visits</h2>
            </div>
            <div className="grid gap-4 xl:grid-cols-2">
              <Bars title="Diagnosis, as stored" unit="Count of cases" rows={library.diagnoses} />
              <Bars title="Decision, as stored" unit="Count of cases" rows={library.decisions} />
            </div>
            <Card>
              <div className="flex flex-wrap items-end justify-between gap-3">
                <div>
                  <h3 className="font-display font-semibold text-3xl">The case rows</h3>
                  <p className="mt-1 text-sm text-[#5c5348] dark:text-[#d9d0c5]">{cases.length} of {library.cases.length} shown. Search matches the stored text.</p>
                </div>
                <input
                  className="h-11 w-full max-w-sm rounded-full border border-[#eadfd2] bg-white px-4 text-sm dark:border-white/10 dark:bg-[#0b1220]"
                  placeholder="Search a symptom, diagnosis, or case"
                  value={caseQuery}
                  onChange={(event) => setCaseQuery(event.target.value)}
                />
              </div>
              <div className="mt-4 max-h-[32rem] overflow-auto rounded-2xl border border-[#eadfd2] dark:border-white/10">
                <table className="w-full min-w-[920px] border-collapse text-left text-sm">
                  <thead className="sticky top-0 bg-[#f7f4ef] text-xs uppercase tracking-[0.14em] text-[#8a6a3b] dark:bg-[#121a2b]">
                    <tr>
                      {["Case", "Age", "Sex", "Symptoms", "Risk factors", "Tests", "Diagnosis", "Decision", "Outcome"].map((heading) => (
                        <th key={heading} className="px-3 py-3 font-medium">{heading}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {cases.map((row) => (
                      <tr key={String(row.case_id)} className="border-t border-[#eadfd2] align-top dark:border-white/10">
                        <td className="px-3 py-3 font-medium">{row.case_id}</td>
                        <td className="px-3 py-3">{shown(row.age)}</td>
                        <td className="px-3 py-3">{shown(row.sex)}</td>
                        <td className="px-3 py-3">{shown(row.symptoms)}</td>
                        <td className="px-3 py-3">{shown(row.risk_factors)}</td>
                        <td className="px-3 py-3">{shown(row.tests)}</td>
                        <td className="px-3 py-3">{shown(row.diagnosis)}</td>
                        <td className="px-3 py-3">{shown(row.treatment_decision)}</td>
                        <td className="px-3 py-3">{shown(row.outcome)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          </section>

          <section className="space-y-4">
            <div>
              <p className="text-xs uppercase tracking-[0.18em] text-[#8a6a3b]">patient_profiles.csv · patient_timelines.csv</p>
              <h2 className="mt-1 font-display font-semibold text-4xl">One profile, and every dated measurement</h2>
            </div>
            <div className="grid gap-4 lg:grid-cols-[280px_1fr]">
              <Card className="lg:max-h-[44rem]">
                <input
                  className="h-11 w-full rounded-full border border-[#eadfd2] bg-white px-4 text-sm dark:border-white/10 dark:bg-[#0b1220]"
                  placeholder="Find a profile"
                  value={profileQuery}
                  onChange={(event) => setProfileQuery(event.target.value)}
                />
                <ul className="mt-3 max-h-[36rem] space-y-1 overflow-auto">
                  {profiles.map((patient) => (
                    <li key={patient.patient_id}>
                      <button
                        className={`w-full rounded-2xl px-3 py-2 text-left text-sm transition ${selected === String(patient.patient_id) ? "bg-[#172033] text-[#f7f4ef]" : "hover:bg-[#f4efe8] dark:hover:bg-white/5"}`}
                        onClick={() => setSelected(String(patient.patient_id))}
                      >
                        <span className="block font-medium">{patient.patient_id}</span>
                        <span className="block text-xs opacity-80">{patient.chief_complaint}</span>
                      </button>
                    </li>
                  ))}
                </ul>
              </Card>
              <div className="space-y-4">
                {current && (
                  <Card>
                    <p className="text-xs uppercase tracking-[0.18em] text-[#8a6a3b]">Stored profile</p>
                    <h3 className="mt-1 font-display font-semibold text-4xl">{current.patient_id}</h3>
                    <dl className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                      {[
                        ["Age", current.age],
                        ["Sex", current.sex],
                        ["LDL", current.ldl],
                        ["HbA1c", current.hba1c],
                        ["Chief complaint", current.chief_complaint],
                        ["History", current.history],
                        ["Medicines", current.medications],
                      ].map(([label, value]) => (
                        <div key={String(label)} className="rounded-2xl bg-[#f7f4ef] px-3 py-3 dark:bg-white/5">
                          <dt className="text-[11px] uppercase tracking-[0.16em] text-[#8a6a3b]">{label}</dt>
                          <dd className="mt-1 text-sm leading-6">{shown(value)}</dd>
                        </div>
                      ))}
                    </dl>
                  </Card>
                )}
                {!visits && <Skeleton className="h-72" />}
                {visits && chart.length === 0 && <Card>No dated rows in patient_timelines.csv for {selected}.</Card>}
                {chart.length > 0 && (
                  <>
                    <MeasureChart
                      title="Blood pressure"
                      unit="mmHg"
                      source={`patient_timelines.csv · ${selected} · ${chart.length} visits`}
                      data={chart}
                      lines={[
                        { key: "systolic", name: "Systolic", color: "#172033" },
                        { key: "diastolic", name: "Diastolic", color: "#b8956a" },
                      ]}
                    />
                    <div className="grid gap-4 xl:grid-cols-2">
                      <MeasureChart
                        title="HbA1c"
                        unit="Percent"
                        source={`patient_timelines.csv · ${selected}`}
                        data={chart}
                        lines={[{ key: "hba1c", name: "HbA1c", color: "#172033" }]}
                      />
                      <MeasureChart
                        title="Weight"
                        unit="Kilograms"
                        source={`patient_timelines.csv · ${selected}`}
                        data={chart}
                        lines={[{ key: "weight", name: "Weight", color: "#8a6a3b" }]}
                      />
                    </div>
                    <Card>
                      <h3 className="font-display font-semibold text-3xl">Exact visit rows</h3>
                      <div className="mt-4 overflow-auto">
                        <table className="w-full min-w-[640px] border-collapse text-left text-sm">
                          <thead className="text-xs uppercase tracking-[0.14em] text-[#8a6a3b]">
                            <tr>
                              {["Date", "Systolic", "Diastolic", "HbA1c", "Weight kg"].map((heading) => (
                                <th key={heading} className="px-3 py-2 font-medium">{heading}</th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {(visits || []).map((visit) => (
                              <tr key={String(visit.date)} className="border-t border-[#eadfd2] dark:border-white/10">
                                <td className="px-3 py-2">{shown(visit.date)}</td>
                                <td className="px-3 py-2">{shown(visit.systolic_bp)}</td>
                                <td className="px-3 py-2">{shown(visit.diastolic_bp)}</td>
                                <td className="px-3 py-2">{shown(visit.hba1c)}</td>
                                <td className="px-3 py-2">{shown(visit.weight_kg)}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </Card>
                  </>
                )}
              </div>
            </div>
          </section>

          <section className="space-y-4">
            <div>
              <p className="text-xs uppercase tracking-[0.18em] text-[#8a6a3b]">graph_nodes.csv · graph_edges.csv</p>
              <h2 className="mt-1 font-display font-semibold text-4xl">{library.nodes.length} names, {library.edges.length} links</h2>
              <p className="mt-2 max-w-3xl text-sm leading-6 text-[#5c5348] dark:text-[#d9d0c5]">The type and the relation are the words stored in the files. The twin matches a patient phrase to a node name, then reads the edges that touch it.</p>
            </div>
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {nodeGroups.map(([type, nodes]) => (
                <Card key={type}>
                  <p className="text-xs uppercase tracking-[0.18em] text-[#8a6a3b]">{type}</p>
                  <ul className="mt-3 space-y-2 text-sm">
                    {nodes.map((node) => (
                      <li key={String(node.node_id)} className="flex justify-between gap-3 border-b border-[#eadfd2] py-1.5 last:border-0 dark:border-white/10">
                        <span>{node.name}</span>
                        <span className="text-[#8a6a3b]">{node.node_id}</span>
                      </li>
                    ))}
                  </ul>
                </Card>
              ))}
            </div>
            <Card>
              <div className="flex flex-wrap gap-2">
                {relations.map((item) => (
                  <button
                    key={item}
                    className={`rounded-full px-3 py-1.5 text-sm ${relation === item ? "bg-[#172033] text-[#f7f4ef]" : "border border-[#eadfd2] dark:border-white/10"}`}
                    onClick={() => setRelation(item)}
                  >
                    {item}
                  </button>
                ))}
              </div>
              <ul className="mt-4 max-h-80 space-y-2 overflow-auto text-sm">
                {visibleEdges.map((edge) => (
                  <li key={`${edge.source_id}-${edge.relation}-${edge.target_id}`} className="rounded-2xl bg-[#f7f4ef] px-3 py-2 dark:bg-white/5">
                    <span className="font-medium">{edge.source_name}</span>
                    <span className="px-2 text-[#8a6a3b]">{edge.relation}</span>
                    <span className="font-medium">{edge.target_name}</span>
                  </li>
                ))}
              </ul>
            </Card>
          </section>

          <section>
            <p className="text-xs uppercase tracking-[0.18em] text-[#8a6a3b]">doctor_style_examples.csv</p>
            <h2 className="mt-1 font-display font-semibold text-4xl">How the twin is asked to sound</h2>
            <div className="mt-4 grid gap-3 md:grid-cols-2">
              {library.style.map((rule) => (
                <Card key={String(rule.example_id)} className="flex gap-4">
                  <span className="font-display font-semibold text-3xl text-[#b8956a]">{rule.example_id}</span>
                  <p className="pt-1 text-lg leading-7">{rule.style_rule}</p>
                </Card>
              ))}
            </div>
          </section>
        </>
      )}
    </div>
  );
}
