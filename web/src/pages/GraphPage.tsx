import { useEffect, useMemo, useRef, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { Maximize2, Minimize2 } from "lucide-react";
import { toast } from "sonner";
import { Button, Card, PageHeader, Skeleton } from "../components/ui";
import { postJson } from "../lib/api";
import { useAppStore } from "../store/useAppStore";

interface GraphNode {
  id: string;
  name?: string;
  label?: string;
  category?: string;
}

interface GraphPayload {
  nodes: GraphNode[];
  edges: Array<{ source: string; target: string; relation?: string }>;
  evidence_summary: string[];
}

type Kind = "symptom" | "risk" | "condition" | "test" | "action";

interface GraphLink {
  source: string;
  target: string;
  relation: string;
}

interface Pos {
  x: number;
  y: number;
  kind: Kind;
}

const KINDS: Array<{ id: Kind; label: string; color: string }> = [
  { id: "symptom", label: "Symptom", color: "#38bdf8" },
  { id: "risk", label: "Risk", color: "#fbbf24" },
  { id: "condition", label: "Condition", color: "#fb7185" },
  { id: "test", label: "Test", color: "#34d399" },
  { id: "action", label: "Action", color: "#a78bfa" },
];

const KIND_COLOR = Object.fromEntries(KINDS.map((kind) => [kind.id, kind.color])) as Record<Kind, string>;

const NODE_W = 172;
const NODE_H = 30;
const BOX_GAP = 12;

function kindOf(name: string): Kind {
  const text = name.toLowerCase();
  if (/ecg|echo|holter|stress test|angiography|lipid panel/.test(text)) return "test";
  if (/referral|optimization|counseling|follow-up|preventive|escalat/.test(text)) return "action";
  if (/^(cad|angina|arrhythmia|heart failure)$/.test(text)) return "condition";
  if (/diabetes|hypertension|smoker|ldl|obesity|family history|sedentary|ckd/.test(text)) return "risk";
  return "symptom";
}

function relationLabel(relation: string): string {
  const known: Record<string, string> = {
    suggests: "suggests",
    increases_risk: "raises risk of",
    managed_by: "is managed by",
    preferred_for: "is preferred for",
    linked_to: "is linked to",
  };
  return known[relation] || relation.split("_").join(" ");
}

function nodeName(node: GraphNode): string {
  return node.label || node.name || node.id;
}

function parseEvidence(lines: string[]): Set<string> {
  const keys = new Set<string>();
  for (const line of lines) {
    const match = line.match(/^(.+?) -> (.+?) \(([^)]+)\)$/);
    if (!match) continue;
    keys.add(`${match[1].trim()}|${match[2].trim()}`);
  }
  return keys;
}

function layoutOf(names: string[]) {
  const grouped = KINDS.map((kind) => names.filter((name) => kindOf(name) === kind.id).sort((a, b) => a.localeCompare(b)));
  const positions = new Map<string, Pos>();
  const home = new Map<string, { x: number; y: number }>();
  const ring = 310;

  grouped.forEach((group, index) => {
    if (!group.length) return;
    const angle = -Math.PI / 2 + (index * 2 * Math.PI) / KINDS.length;
    const cx = Math.cos(angle) * ring;
    const cy = Math.sin(angle) * ring;
    const tangent = angle + Math.PI / 2;
    group.forEach((name, item) => {
      const col = item % 2;
      const row = Math.floor(item / 2);
      const along = (row - (group.length / 4)) * (NODE_H + BOX_GAP);
      const outward = (col === 0 ? -0.55 : 0.55) * (NODE_W * 0.72);
      const x = cx + Math.cos(tangent) * along + Math.cos(angle) * outward - NODE_W / 2;
      const y = cy + Math.sin(tangent) * along + Math.sin(angle) * outward - NODE_H / 2;
      positions.set(name, { x, y, kind: KINDS[index].id });
      home.set(name, { x, y });
    });
  });

  const items = [...positions.entries()];
  const minXGap = NODE_W + BOX_GAP;
  const minYGap = NODE_H + BOX_GAP;
  for (let iter = 0; iter < 48; iter += 1) {
    for (const [name, pos] of items) {
      const origin = home.get(name);
      if (!origin) continue;
      pos.x += (origin.x - pos.x) * 0.05;
      pos.y += (origin.y - pos.y) * 0.05;
    }
    for (let i = 0; i < items.length; i += 1) {
      for (let j = i + 1; j < items.length; j += 1) {
        const a = items[i][1];
        const b = items[j][1];
        const dx = b.x - a.x;
        const dy = b.y - a.y;
        if (Math.abs(dx) >= minXGap || Math.abs(dy) >= minYGap) continue;
        const overlapX = minXGap - Math.abs(dx);
        const overlapY = minYGap - Math.abs(dy);
        if (overlapX < overlapY) {
          const push = overlapX / 2 + 0.4;
          const sign = dx < 0 ? -1 : 1;
          a.x -= sign * push;
          b.x += sign * push;
        } else {
          const push = overlapY / 2 + 0.4;
          const sign = dy < 0 ? -1 : 1;
          a.y -= sign * push;
          b.y += sign * push;
        }
      }
    }
  }

  let minX = Infinity;
  let minY = Infinity;
  let maxX = 0;
  let maxY = 0;
  for (const pos of positions.values()) {
    minX = Math.min(minX, pos.x);
    minY = Math.min(minY, pos.y);
  }
  for (const pos of positions.values()) {
    pos.x = pos.x - minX + 28;
    pos.y = pos.y - minY + 28;
    maxX = Math.max(maxX, pos.x + NODE_W);
    maxY = Math.max(maxY, pos.y + NODE_H);
  }
  return { positions, width: maxX + 28, height: maxY + 28 };
}

function centerOf(pos: Pos) {
  return { x: pos.x + NODE_W / 2, y: pos.y + NODE_H / 2 };
}

function rim(from: { x: number; y: number }, to: { x: number; y: number }) {
  const dx = to.x - from.x;
  const dy = to.y - from.y;
  const tx = dx === 0 ? Infinity : (NODE_W / 2) / Math.abs(dx);
  const ty = dy === 0 ? Infinity : (NODE_H / 2) / Math.abs(dy);
  const t = Math.min(tx, ty);
  return { x: from.x + dx * t, y: from.y + dy * t };
}

function PatientGraph({ payload, dark, patientName }: { payload: GraphPayload; dark: boolean; patientName: string }) {
  const model = useMemo(() => {
    const names = new Map(payload.nodes.map((node) => [String(node.id), nodeName(node)]));
    const links: GraphLink[] = [];
    const seen = new Set<string>();
    for (const edge of payload.edges) {
      const source = names.get(String(edge.source)) || String(edge.source);
      const target = names.get(String(edge.target)) || String(edge.target);
      const relation = edge.relation || "linked_to";
      const key = `${source}|${target}|${relation}`;
      if (seen.has(key) || source === target) continue;
      seen.add(key);
      links.push({ source, target, relation });
    }
    const unique = [...new Set(links.flatMap((link) => [link.source, link.target]))];
    const focus = parseEvidence(payload.evidence_summary);
    const patientLinks = links.filter((link) => focus.has(`${link.source}|${link.target}`));
    const patientNames = [...new Set(patientLinks.flatMap((link) => [link.source, link.target]))];
    return {
      links,
      patientLinks,
      layout: layoutOf(unique),
      patientLayout: patientNames.length ? layoutOf(patientNames) : { positions: new Map<string, Pos>(), width: 1, height: 1 },
      focus,
    };
  }, [payload]);

  const [params] = useSearchParams();
  const [scope, setScope] = useState<"patient" | "all">(params.get("scope") === "all" ? "all" : "patient");
  useEffect(() => {
    setScope(params.get("scope") === "all" ? "all" : "patient");
  }, [params]);
  const showingPatient = scope === "patient";
  const links = showingPatient ? model.patientLinks : model.links;
  const layout = showingPatient ? model.patientLayout : model.layout;
  const focus = model.focus;
  const [selected, setSelected] = useState<string | null>(null);
  const [view, setView] = useState({ zoom: 1, x: 0, y: 0 });
  const [cssFull, setCssFull] = useState(false);
  const [nativeFull, setNativeFull] = useState(false);
  const viewRef = useRef(view);
  const frameRef = useRef<HTMLDivElement>(null);
  const drag = useRef<{ x: number; y: number; panX: number; panY: number } | null>(null);
  const pointers = useRef(new Map<number, { x: number; y: number }>());
  const pinch = useRef<{ dist: number; zoom: number } | null>(null);
  viewRef.current = view;
  const expanded = cssFull || nativeFull;

  useEffect(() => {
    const frame = frameRef.current;
    if (!frame) return;
    const onWheel = (event: WheelEvent) => {
      event.preventDefault();
      const rect = frame.getBoundingClientRect();
      const px = event.clientX - rect.left - rect.width / 2;
      const py = event.clientY - rect.top - rect.height / 2;
      const current = viewRef.current;
      const nextZoom = Math.min(2.8, Math.max(0.55, current.zoom * (event.deltaY < 0 ? 1.12 : 1 / 1.12)));
      const scale = nextZoom / current.zoom;
      const next = { zoom: nextZoom, x: px - (px - current.x) * scale, y: py - (py - current.y) * scale };
      viewRef.current = next;
      setView(next);
    };
    frame.addEventListener("wheel", onWheel, { passive: false });
    return () => frame.removeEventListener("wheel", onWheel);
  }, []);

  useEffect(() => {
    const sync = () => setNativeFull(document.fullscreenElement === frameRef.current);
    document.addEventListener("fullscreenchange", sync);
    return () => document.removeEventListener("fullscreenchange", sync);
  }, []);

  useEffect(() => {
    document.body.style.overflow = cssFull ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [cssFull]);

  const ink = dark ? "#f8fafc" : "#0f172a";
  const selectedLinks = selected ? links.filter((link) => link.source === selected || link.target === selected) : [];
  const focusNodes = new Set<string>();
  for (const key of focus) {
    const [source, target] = key.split("|");
    focusNodes.add(source);
    focusNodes.add(target);
  }

  function show(nextScope: "patient" | "all") {
    setScope(nextScope);
    setSelected(null);
    const next = { zoom: 1, x: 0, y: 0 };
    viewRef.current = next;
    setView(next);
  }

  function zoomBy(factor: number) {
    setView((current) => {
      const next = { ...current, zoom: Math.min(2.8, Math.max(0.55, current.zoom * factor)) };
      viewRef.current = next;
      return next;
    });
  }

  function applyPinch() {
    if (!pinch.current || pointers.current.size < 2) return false;
    const [a, b] = [...pointers.current.values()];
    const dist = Math.hypot(a.x - b.x, a.y - b.y) || 1;
    const zoom = Math.min(2.8, Math.max(0.55, pinch.current.zoom * (dist / pinch.current.dist)));
    const next = { ...viewRef.current, zoom };
    viewRef.current = next;
    setView(next);
    return true;
  }

  async function toggleFull() {
    const frame = frameRef.current;
    if (!frame) return;
    if (document.fullscreenElement || cssFull) {
      if (document.fullscreenElement) {
        try {
          await document.exitFullscreen();
        } catch {
          setCssFull(false);
        }
      }
      setCssFull(false);
      return;
    }
    try {
      await frame.requestFullscreen();
    } catch {
      setCssFull(true);
    }
  }

  function linkActive(link: GraphLink) {
    if (selected) return link.source === selected || link.target === selected;
    if (showingPatient) return true;
    return focus.has(`${link.source}|${link.target}`);
  }

  return (
    <div>
      <div className="mb-3 inline-flex rounded-xl border border-slate-200 bg-slate-100 p-1 dark:border-white/10 dark:bg-white/5" role="group" aria-label="Graph scope">
        <button type="button" aria-pressed={showingPatient} className={`rounded-lg px-3 py-1.5 text-sm font-semibold ${showingPatient ? "bg-sky-500 text-slate-950" : "text-slate-600 dark:text-slate-300"}`} onClick={() => show("patient")}>{patientName}</button>
        <button type="button" aria-pressed={!showingPatient} className={`rounded-lg px-3 py-1.5 text-sm font-semibold ${!showingPatient ? "bg-sky-500 text-slate-950" : "text-slate-600 dark:text-slate-300"}`} onClick={() => show("all")}>Entire graph</button>
      </div>
      <div className="mb-3 flex flex-wrap items-center gap-x-4 gap-y-2 text-xs text-slate-500">
        {KINDS.map((kind) => (
          <span key={kind.id} className="inline-flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-full" style={{ background: kind.color }} />
            {kind.label}
          </span>
        ))}
        {!showingPatient && (
          <span className="inline-flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-full border-2 border-sky-400" />
            {patientName}
          </span>
        )}
      </div>
      {links.length > 0 && <div
        ref={frameRef}
        className={`cursor-grab touch-none overflow-hidden border border-slate-200/80 bg-slate-50 active:cursor-grabbing dark:border-white/10 dark:bg-[#0c1424] ${cssFull ? "fixed inset-0 z-50 h-[100dvh] w-screen rounded-none" : expanded ? "relative h-[100dvh] w-full rounded-none" : "relative h-[70vh] min-h-[420px] rounded-2xl md:h-[640px]"}`}
        onPointerDown={(event) => {
          pointers.current.set(event.pointerId, { x: event.clientX, y: event.clientY });
          if (pointers.current.size >= 2) {
            drag.current = null;
            const [a, b] = [...pointers.current.values()];
            pinch.current = { dist: Math.hypot(a.x - b.x, a.y - b.y) || 1, zoom: viewRef.current.zoom };
            return;
          }
          const target = event.target as Element;
          if (target.closest("[data-node]") || target.closest("[data-zoom]")) return;
          drag.current = { x: event.clientX, y: event.clientY, panX: view.x, panY: view.y };
          event.currentTarget.setPointerCapture(event.pointerId);
        }}
        onPointerMove={(event) => {
          if (pointers.current.has(event.pointerId)) pointers.current.set(event.pointerId, { x: event.clientX, y: event.clientY });
          if (applyPinch()) return;
          if (!drag.current) return;
          const next = { ...viewRef.current, x: drag.current.panX + event.clientX - drag.current.x, y: drag.current.panY + event.clientY - drag.current.y };
          viewRef.current = next;
          setView(next);
        }}
        onPointerUp={(event) => {
          pointers.current.delete(event.pointerId);
          if (pointers.current.size < 2) pinch.current = null;
          drag.current = null;
        }}
        onPointerCancel={(event) => {
          pointers.current.delete(event.pointerId);
          if (pointers.current.size < 2) pinch.current = null;
          drag.current = null;
        }}
      >
        <div className="flex h-full w-full items-center justify-center" style={{ transform: `translate(${view.x}px, ${view.y}px) scale(${view.zoom})` }}>
          <svg viewBox={`0 0 ${layout.width} ${layout.height}`} className="h-full w-full" role="img" aria-label="Knowledge graph">
            <defs>
              <marker id="graph-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 1.2 L 8 5 L 0 8.8 z" fill={dark ? "#7dd3fc" : "#0284c7"} />
              </marker>
            </defs>
            {links.map((link, index) => {
              const source = layout.positions.get(link.source);
              const target = layout.positions.get(link.target);
              if (!source || !target) return null;
              const a = centerOf(source);
              const b = centerOf(target);
              const start = rim(a, b);
              const end = rim(b, a);
              const mx = (start.x + end.x) / 2;
              const my = (start.y + end.y) / 2;
              const dx = end.x - start.x;
              const dy = end.y - start.y;
              const len = Math.hypot(dx, dy) || 1;
              const bend = ((index % 5) - 2) * 14;
              const active = linkActive(link);
              return (
                <path
                  key={`${link.source}-${link.target}-${link.relation}`}
                  d={`M ${start.x} ${start.y} Q ${mx - (dy / len) * bend} ${my + (dx / len) * bend} ${end.x} ${end.y}`}
                  fill="none"
                  stroke={active ? (dark ? "#7dd3fc" : "#0284c7") : (dark ? "#64748b" : "#94a3b8")}
                  strokeWidth={active ? 1.7 : 1}
                  opacity={selected ? (active ? 0.95 : 0.08) : active ? 0.85 : 0.22}
                  markerEnd={active ? "url(#graph-arrow)" : undefined}
                />
              );
            })}
            {[...layout.positions.entries()].map(([name, pos]) => {
              const on = !selected || selected === name || selectedLinks.some((link) => link.source === name || link.target === name);
              const patient = focusNodes.has(name);
              return (
                <g
                  key={name}
                  data-node="true"
                  role="button"
                  tabIndex={0}
                  aria-pressed={selected === name}
                  aria-label={name}
                  style={{ cursor: "pointer" }}
                  opacity={on ? 1 : 0.28}
                  onPointerDown={(event) => event.stopPropagation()}
                  onClick={() => setSelected((current) => (current === name ? null : name))}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" || event.key === " ") {
                      event.preventDefault();
                      setSelected((current) => (current === name ? null : name));
                    }
                  }}
                >
                  <rect
                    x={pos.x}
                    y={pos.y}
                    width={NODE_W}
                    height={NODE_H}
                    rx="10"
                    fill={dark ? "#162033" : "#ffffff"}
                    stroke={!showingPatient && patient ? "#38bdf8" : KIND_COLOR[pos.kind]}
                    strokeWidth={selected === name ? 2.6 : !showingPatient && patient ? 2.2 : 1.4}
                  />
                  <text x={pos.x + NODE_W / 2} y={pos.y + 20} textAnchor="middle" fill={ink} fontSize="11" fontWeight="600">
                    {name}
                  </text>
                </g>
              );
            })}
          </svg>
        </div>
        <div data-zoom="true" className="absolute right-3 top-3 flex flex-col gap-1">
          <button type="button" aria-label="Zoom in" className="h-11 w-11 rounded-lg border border-slate-300 bg-white text-lg font-semibold text-[#0b1f3a] dark:border-white/15 dark:bg-[#111a2e] dark:text-white" onClick={() => zoomBy(1.2)}>+</button>
          <button type="button" aria-label="Zoom out" className="h-11 w-11 rounded-lg border border-slate-300 bg-white text-lg font-semibold text-[#0b1f3a] dark:border-white/15 dark:bg-[#111a2e] dark:text-white" onClick={() => zoomBy(1 / 1.2)}>−</button>
          <button type="button" aria-label="Fit graph" className="h-11 w-11 rounded-lg border border-slate-300 bg-white text-[11px] font-semibold text-[#0b1f3a] dark:border-white/15 dark:bg-[#111a2e] dark:text-white" onClick={() => { const next = { zoom: 1, x: 0, y: 0 }; viewRef.current = next; setView(next); }}>Fit</button>
          <button type="button" aria-label={expanded ? "Exit full screen" : "Full screen"} className="inline-flex h-11 w-11 items-center justify-center rounded-lg border border-slate-300 bg-white text-[#0b1f3a] dark:border-white/15 dark:bg-[#111a2e] dark:text-white" onClick={() => void toggleFull()}>
            {expanded ? <Minimize2 size={18} /> : <Maximize2 size={18} />}
          </button>
        </div>
      </div>}
      <div className="mt-3 min-h-8">
        {!selected && showingPatient && links.length === 0 && <p className="text-sm text-slate-500">No graph links were triggered for {patientName}. Switch to Entire graph to see the full map.</p>}
        {!selected && links.length > 0 && <p className="text-sm text-slate-500">{showingPatient ? `${patientName}: ` : "Entire graph: "}{layout.positions.size} names, {links.length} links. Drag to move. Pinch, scroll, or use + and − to zoom. Full screen fills the phone.{showingPatient ? "" : ` Bright lines belong to ${patientName}.`}</p>}
        {selected && (
          <div className="flex flex-wrap gap-2">
            {selectedLinks.slice(0, 8).map((link) => (
              <p key={`${link.source}-${link.target}-${link.relation}`} className="rounded-full border border-slate-200 px-3 py-1 text-sm dark:border-white/10">
                <span className="font-semibold">{link.source}</span>
                <span className="mx-1.5 text-sky-600 dark:text-sky-300">{relationLabel(link.relation)}</span>
                <span className="font-semibold">{link.target}</span>
              </p>
            ))}
            {selectedLinks.length > 8 && <p className="self-center text-xs text-slate-500">+{selectedLinks.length - 8} more</p>}
          </div>
        )}
      </div>
    </div>
  );
}

export default function GraphPage() {
  const patient = useAppStore((s) => s.patient);
  const dark = useAppStore((s) => s.theme === "dark");
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const fromConsultation = params.get("from") === "consultation";
  const [payload, setPayload] = useState<GraphPayload | null>(null);

  useEffect(() => {
    if (!patient) return;
    postJson<GraphPayload>("/api/evidence/graph", patient)
      .then(setPayload)
      .catch((error: Error) => toast.error(error.message));
  }, [patient]);

  if (!patient) return <Card><p>Please complete Patient Intake first.</p><Link to="/patient" className="text-sky-600">Open intake</Link></Card>;

  return (
    <div>
      <PageHeader eyebrow="7 · Graph" title="Graph Intelligence" caption="Switch between this patient's links and the full cardiology graph. Drag it like a map." />
      {fromConsultation && <Button className="mb-4" variant="primary" onClick={() => navigate("/consultation")}>Back to consultation</Button>}
      {!payload && <Skeleton className="h-[640px]" />}
      {payload && (
        <Card>
          <PatientGraph payload={payload} dark={dark} patientName={patient.name} />
        </Card>
      )}
      <Button className="mt-4" variant="primary" onClick={() => navigate("/why")}>See why this plan</Button>
    </div>
  );
}
