import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import ForceGraph2D from "react-force-graph-2d";
import { BulletList, Button, Card, Note, PageHeader, Skeleton } from "../components/ui";
import { postJson } from "../lib/api";
import { useAppStore } from "../store/useAppStore";

interface GraphPayload {
  nodes: Array<{ id: string; name?: string; label?: string; category?: string }>;
  edges: Array<{ source: string; target: string; relation?: string }>;
  evidence_summary: string[];
}

export default function GraphPage() {
  const patient = useAppStore((s) => s.patient);
  const navigate = useNavigate();
  const [payload, setPayload] = useState<GraphPayload | null>(null);
  const [query, setQuery] = useState("");

  useEffect(() => {
    if (!patient) return;
    postJson<GraphPayload>("/api/evidence/graph", patient)
      .then(setPayload)
      .catch((error: Error) => toast.error(error.message));
  }, [patient]);

  if (!patient) return <Card><p>Please complete Patient Intake first.</p><Link to="/patient" className="text-sky-600">Open intake</Link></Card>;
  const graph = payload ? {
    nodes: payload.nodes.map((node) => ({ ...node, name: node.label || node.name || node.id })),
    links: payload.edges.map((edge) => ({ source: edge.source, target: edge.target, relation: edge.relation || "linked_to" })),
  } : null;
  const preview = (payload?.edges || []).slice(0, 5);
  const nameOf = (id: string) => payload?.nodes.find((node) => node.id === id)?.name || payload?.nodes.find((node) => node.id === id)?.label || id;
  const filtered = (payload?.edges || []).filter((edge) => `${nameOf(edge.source)} ${nameOf(edge.target)} ${edge.relation}`.toLowerCase().includes(query.toLowerCase()));
  return (
    <div>
      <PageHeader eyebrow="7 · Graph" title="Graph Intelligence" caption="Relationship intelligence across symptoms, risks, tests, and decisions." />
      <Note title="How to interpret the graph">Nodes are clinical entities from the uploaded graph. Edges show direction and relationship type. Drag nodes, scroll to zoom, and hover for names.</Note>
      {!payload && <Skeleton className="h-[640px]" />}
      {graph && (
        <Card className="h-[680px] overflow-hidden p-2">
          <ForceGraph2D
            graphData={graph}
            height={640}
            nodeLabel="name"
            nodeAutoColorBy="category"
            linkDirectionalArrowLength={4}
            linkDirectionalArrowRelPos={1}
            linkLabel="relation"
            cooldownTicks={80}
          />
        </Card>
      )}
      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        <Card>
          <h2 className="font-semibold">Graph evidence summary</h2>
          <div className="mt-3"><BulletList items={payload?.evidence_summary} /></div>
        </Card>
        <Card>
          <h2 className="font-semibold">Highlighted links</h2>
          <ul className="mt-3 space-y-1 text-sm">
            {preview.map((edge, index) => <li key={index}>{nameOf(edge.source)} → {nameOf(edge.target)} ({edge.relation || "linked_to"})</li>)}
          </ul>
          <input className="mt-3 w-full rounded-xl border border-slate-300 bg-transparent px-3 py-2 text-sm dark:border-white/15" placeholder="Filter all links" value={query} onChange={(e) => setQuery(e.target.value)} />
          <ul className="mt-2 max-h-40 space-y-1 overflow-auto text-xs text-slate-500">
            {filtered.slice(0, 30).map((edge, index) => <li key={index}>{nameOf(edge.source)} → {nameOf(edge.target)} ({edge.relation})</li>)}
          </ul>
        </Card>
      </div>
      <Button className="mt-4" variant="primary" onClick={() => navigate("/insights")}>Open Comparison Insights</Button>
    </div>
  );
}
