"use client";

import {
  Activity,
  ArrowRightLeft,
  Binary,
  Check,
  Copy,
  Database,
  Dna,
  Download,
  Loader2,
  Search,
  Sparkles,
  Zap,
} from "lucide-react";
import { FormEvent, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type TabKey = "embed" | "compare" | "search" | "cache";
type ProteinInputMode = "accession" | "sequence";

type EmbeddingResponse = {
  source: string;
  sequence_length: number;
  embedding_dim: number;
  cache_status: string;
  embedding_preview: number[];
  vector?: number[] | null;
  model_name: string;
  backend: string;
};

type CompareResponse = {
  left: ResolvedProteinInput;
  right: ResolvedProteinInput;
  cosine_similarity: number;
  left_cache_status: string;
  right_cache_status: string;
  interpretation: string;
  embedding_backend: string;
  is_biologically_meaningful: boolean;
  warning?: string | null;
};

type ResolvedProteinInput = {
  source: string;
  accession?: string | null;
  protein_name?: string | null;
  organism?: string | null;
  sequence_length: number;
};

type CacheStatsResponse = {
  total_embeddings: number;
  backend: string;
  model_name: string;
};

type SimilarSearchResponse = {
  query: ResolvedProteinInput;
  query_cache_status: string;
  backend: string;
  model_name: string;
  matches: Array<{
    source?: string | null;
    accession?: string | null;
    protein_name?: string | null;
    organism?: string | null;
    sequence_length?: number | null;
    similarity: number;
    created_at?: string | null;
  }>;
};

const tabs: Array<{ key: TabKey; label: string; icon: typeof Zap }> = [
  { key: "embed", label: "Embed", icon: Zap },
  { key: "compare", label: "Compare", icon: ArrowRightLeft },
  { key: "search", label: "Search", icon: Search },
  { key: "cache", label: "Cache", icon: Database },
];

async function postJson<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new Error(payload?.detail ?? `Request failed with ${response.status}`);
  }

  return response.json();
}

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`);

  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new Error(payload?.detail ?? `Request failed with ${response.status}`);
  }

  return response.json();
}

function buildProteinPayload(mode: ProteinInputMode, value: string) {
  const trimmed = value.trim();
  if (mode === "sequence") {
    return { sequence: trimmed };
  }

  return /^[A-Z0-9]{6,10}$/i.test(trimmed)
    ? { accession: trimmed }
    : { protein_name: trimmed };
}

export default function Home() {
  const [activeTab, setActiveTab] = useState<TabKey>("embed");

  return (
    <main className="min-h-screen text-foreground">
      <div className="mx-auto flex min-h-screen w-full max-w-[1440px] flex-col px-6 py-10 sm:px-10 lg:px-14">
        <header className="flex flex-col gap-6 border-b border-hairline pb-10 xl:flex-row xl:items-end xl:justify-between">
          <div className="flex min-w-0 items-center gap-4">
            <div className="grid size-11 place-items-center rounded-md bg-ink text-white">
              <Dna size={20} strokeWidth={1.75} />
            </div>
            <div className="min-w-0">
              <p className="text-[10px] uppercase tracking-[0.22em] text-caption">
                Protein Embedding Workbench
              </p>
              <h1 className="mt-1.5 font-heading text-5xl font-bold tracking-tight text-ink">
                Semantic protein explorer
              </h1>
            </div>
          </div>

          <div className="flex shrink-0 flex-wrap items-center justify-start gap-2 xl:justify-end">
            <StatusPill icon={Activity} label="FastAPI" value={API_BASE} />
            <StatusPill icon={Sparkles} label="Vector cache" value="visible" />
          </div>
        </header>

        <section className="grid flex-1 gap-12 py-10 lg:grid-cols-[200px_minmax(0,1fr)]">
          <nav className="flex gap-1 overflow-x-auto pb-2 lg:flex-col lg:gap-0 lg:overflow-visible lg:border-r lg:border-hairline lg:pb-0 lg:pr-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const active = activeTab === tab.key;
              return (
                <button
                  key={tab.key}
                  type="button"
                  onClick={() => setActiveTab(tab.key)}
                  className={`relative flex h-10 cursor-pointer items-center gap-2.5 px-4 text-sm font-medium transition lg:h-11 lg:w-full lg:justify-start lg:border-l-2 lg:px-5 ${
                    active
                      ? "text-ink lg:border-accent"
                      : "text-muted hover:text-ink lg:border-transparent"
                  }`}
                >
                  <Icon size={15} strokeWidth={1.5} />
                  {tab.label}
                </button>
              );
            })}
          </nav>

          <div className="min-w-0">
            {activeTab === "embed" && <EmbedPanel />}
            {activeTab === "compare" && <ComparePanel />}
            {activeTab === "search" && <SearchPanel />}
            {activeTab === "cache" && <CachePanel />}
          </div>
        </section>
      </div>
    </main>
  );
}

function EmbedPanel() {
  const [mode, setMode] = useState<ProteinInputMode>("accession");
  const [value, setValue] = useState("P69905");
  const [includeVector, setIncludeVector] = useState(false);
  const [result, setResult] = useState<EmbeddingResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function generateEmbedding(returnVector = includeVector) {
    setLoading(true);
    setError(null);
    try {
      const payload = {
        ...buildProteinPayload(mode, value),
        include_vector: returnVector,
      };
      setResult(await postJson<EmbeddingResponse>("/api/embeddings", payload));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Embedding failed");
    } finally {
      setLoading(false);
    }
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await generateEmbedding();
  }

  return (
    <WorkspacePanel
      icon={Zap}
      title="Embed"
      toolbar={<CacheBadge status={result?.cache_status} />}
    >
      <form
        onSubmit={submit}
        className="grid items-start gap-8 lg:grid-cols-[minmax(0,0.95fr)_minmax(0,1.05fr)]"
      >
        <ProteinInput
          mode={mode}
          value={value}
          onModeChange={setMode}
          onValueChange={setValue}
        />
        <div className="flex flex-col gap-4">
          <label className="flex h-10 cursor-pointer items-center justify-between rounded-md border border-hairline bg-white px-4 text-sm text-ink">
            Return full vector
            <input
              type="checkbox"
              checked={includeVector}
              onChange={(event) => {
                const checked = event.target.checked;
                setIncludeVector(checked);
                if (!checked) {
                  setResult((current) =>
                    current ? { ...current, vector: null } : current,
                  );
                  return;
                }
                if (result && !result.vector) {
                  void generateEmbedding(true);
                }
              }}
              className="size-4 accent-ink"
            />
          </label>
          <PrimaryButton loading={loading} label="Generate embedding" icon={Binary} />
          <ErrorMessage message={error} />
          {result && <EmbeddingResult result={result} />}
        </div>
      </form>
    </WorkspacePanel>
  );
}

function ComparePanel() {
  const [leftMode, setLeftMode] = useState<ProteinInputMode>("accession");
  const [rightMode, setRightMode] = useState<ProteinInputMode>("accession");
  const [leftValue, setLeftValue] = useState("P69905");
  const [rightValue, setRightValue] = useState("P68871");
  const [result, setResult] = useState<CompareResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      setResult(
        await postJson<CompareResponse>("/api/compare", {
          left: buildProteinPayload(leftMode, leftValue),
          right: buildProteinPayload(rightMode, rightValue),
        }),
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Comparison failed");
    } finally {
      setLoading(false);
    }
  }

  const scorePercent = Math.max(0, Math.min(100, (result?.cosine_similarity ?? 0) * 100));

  return (
    <WorkspacePanel icon={ArrowRightLeft} title="Compare">
      <form onSubmit={submit} className="grid gap-8">
        <div className="grid items-start gap-8 lg:grid-cols-2">
          <ProteinInput
            label="Left protein"
            mode={leftMode}
            value={leftValue}
            onModeChange={setLeftMode}
            onValueChange={setLeftValue}
          />
          <ProteinInput
            label="Right protein"
            mode={rightMode}
            value={rightValue}
            onModeChange={setRightMode}
            onValueChange={setRightValue}
          />
        </div>
        <div className="max-w-xs">
          <PrimaryButton loading={loading} label="Compare embeddings" icon={ArrowRightLeft} />
        </div>
        <ErrorMessage message={error} />
      </form>

      {result && (
        <section className="mt-10 grid gap-8 lg:grid-cols-[300px_minmax(0,1fr)]">
          <div className="rounded-md border border-hairline bg-white p-7">
            <p className="text-xs uppercase tracking-[0.18em] text-caption">
              Cosine similarity
            </p>
            <p className="mt-4 font-heading text-5xl font-bold tracking-tight text-ink">
              {result.cosine_similarity.toFixed(3)}
            </p>
            <div className="mt-6 h-1.5 overflow-hidden rounded-full bg-track">
              <div
                className="h-full rounded-full bg-accent transition-[width]"
                style={{ width: `${scorePercent}%` }}
              />
            </div>
          </div>
          <div className="grid gap-4">
            <div className="grid gap-4 md:grid-cols-2">
              <ProteinSummary protein={result.left} status={result.left_cache_status} />
              <ProteinSummary protein={result.right} status={result.right_cache_status} />
            </div>
            <p className="rounded-md border border-hairline bg-white p-5 text-sm text-muted">
              {result.interpretation}
            </p>
          </div>
        </section>
      )}
    </WorkspacePanel>
  );
}

function SearchPanel() {
  const [mode, setMode] = useState<ProteinInputMode>("accession");
  const [value, setValue] = useState("P69905");
  const [topK, setTopK] = useState(5);
  const [result, setResult] = useState<SimilarSearchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      setResult(
        await postJson<SimilarSearchResponse>("/api/search/similar", {
          ...buildProteinPayload(mode, value),
          top_k: topK,
        }),
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <WorkspacePanel
      icon={Search}
      title="Similarity search"
      toolbar={<CacheBadge status={result?.query_cache_status} />}
    >
      <form
        onSubmit={submit}
        className="grid items-start gap-8 lg:grid-cols-[minmax(0,1fr)_280px]"
      >
        <ProteinInput
          mode={mode}
          value={value}
          onModeChange={setMode}
          onValueChange={setValue}
        />
        <div className="flex flex-col gap-4">
          <label className="grid cursor-pointer gap-2 text-sm text-ink">
            <span className="text-xs uppercase tracking-[0.18em] text-caption">Top K</span>
            <input
              type="number"
              min={1}
              max={100}
              value={topK}
              onChange={(event) => setTopK(Number(event.target.value))}
              className="h-10 rounded-md border border-hairline bg-white px-3 text-base font-normal outline-none transition focus:border-ink"
            />
          </label>
          <PrimaryButton loading={loading} label="Find matches" icon={Search} />
          <ErrorMessage message={error} />
        </div>
      </form>

      {result && (
        <section className="mt-10 grid gap-3">
          {result.matches.length === 0 ? (
            <EmptyState />
          ) : (
            result.matches.map((match, index) => (
              <div
                key={`${match.accession ?? match.source ?? index}-${index}`}
                className="grid gap-4 rounded-md border border-hairline bg-white p-5 transition hover:border-hairline-strong md:grid-cols-[48px_minmax(0,1fr)_120px] md:items-center"
              >
                <p className="font-mono text-sm text-muted">{String(index + 1).padStart(2, "0")}</p>
                <div className="min-w-0">
                  <p className="truncate text-base text-ink">
                    {match.protein_name ?? match.accession ?? match.source ?? "Cached protein"}
                  </p>
                  <p className="mt-1 text-sm text-muted">
                    {[match.accession, match.organism, match.sequence_length && `${match.sequence_length} aa`]
                      .filter(Boolean)
                      .join(" · ")}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-xs uppercase tracking-[0.18em] text-caption">Score</p>
                  <p className="mt-1 font-mono text-2xl font-bold text-ink">
                    {match.similarity.toFixed(3)}
                  </p>
                </div>
              </div>
            ))
          )}
        </section>
      )}
    </WorkspacePanel>
  );
}

function CachePanel() {
  const [stats, setStats] = useState<CacheStatsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadStats() {
    setLoading(true);
    setError(null);
    try {
      setStats(await getJson<CacheStatsResponse>("/api/cache/stats"));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Cache stats failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <WorkspacePanel icon={Database} title="Cache">
      <div className="grid gap-4 md:grid-cols-3">
        <Metric label="Embeddings" value={stats?.total_embeddings ?? "—"} />
        <Metric label="Backend" value={stats?.backend ?? "—"} />
        <Metric label="Model" value={stats?.model_name ?? "—"} />
      </div>
      <div className="mt-8 max-w-xs">
        <PrimaryButton loading={loading} label="Refresh cache stats" icon={Database} onClick={loadStats} />
      </div>
      <ErrorMessage message={error} />
    </WorkspacePanel>
  );
}

function WorkspacePanel({
  icon: Icon,
  title,
  toolbar,
  children,
}: {
  icon: typeof Zap;
  title: string;
  toolbar?: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <section className="rounded-lg border border-hairline bg-white p-10 sm:p-14">
      <div className="mb-12 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Icon size={18} strokeWidth={1.5} className="text-accent" />
          <h2 className="font-heading text-3xl font-bold tracking-tight text-ink">
            {title}
          </h2>
        </div>
        {toolbar}
      </div>
      {children}
    </section>
  );
}

function ProteinInput({
  label = "Protein input",
  mode,
  value,
  onModeChange,
  onValueChange,
}: {
  label?: string;
  mode: ProteinInputMode;
  value: string;
  onModeChange: (mode: ProteinInputMode) => void;
  onValueChange: (value: string) => void;
}) {
  return (
    <div className="grid gap-3">
      <span className="text-xs uppercase tracking-[0.18em] text-caption">{label}</span>
      <div className="inline-flex h-9 self-start overflow-hidden rounded-md border border-hairline">
        {(["accession", "sequence"] as const).map((option) => (
          <button
            key={option}
            type="button"
            onClick={() => onModeChange(option)}
            className={`cursor-pointer px-4 text-sm capitalize transition ${
              mode === option
                ? "bg-ink text-white"
                : "bg-white text-muted hover:text-ink"
            }`}
          >
            {option}
          </button>
        ))}
      </div>
      {mode === "accession" ? (
        <input
          value={value}
          onChange={(event) => onValueChange(event.target.value)}
          className="h-10 rounded-md border border-hairline bg-white px-3 text-base font-normal outline-none transition focus:border-ink"
          placeholder="P69905"
        />
      ) : (
        <textarea
          value={value}
          onChange={(event) => onValueChange(event.target.value)}
          className="min-h-44 resize-y rounded-md border border-hairline bg-white p-3 font-mono text-sm outline-none transition focus:border-ink"
          placeholder="MVLSPADKTNVKAA..."
        />
      )}
    </div>
  );
}

function EmbeddingResult({ result }: { result: EmbeddingResponse }) {
  const [copied, setCopied] = useState(false);
  const fullVector = result.vector ?? null;

  async function copyFullVector() {
    if (!fullVector) return;

    await navigator.clipboard.writeText(JSON.stringify(fullVector));
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1500);
  }

  function downloadFullVector() {
    if (!fullVector) return;

    const payload = {
      source: result.source,
      sequence_length: result.sequence_length,
      embedding_dim: result.embedding_dim,
      backend: result.backend,
      model_name: result.model_name,
      vector: fullVector,
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    const safeSource = result.source.replace(/[^a-z0-9-]+/gi, "_").toLowerCase();

    link.href = url;
    link.download = `${safeSource || "protein"}-embedding.json`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  return (
    <section className="grid gap-5">
      <div className="grid gap-3 sm:grid-cols-3">
        <Metric label="Length" value={result.sequence_length} />
        <Metric label="Dimensions" value={result.embedding_dim} />
        <Metric label="Backend" value={result.backend} />
      </div>
      <div className="rounded-md border border-hairline bg-white p-5">
        <p className="mb-4 text-xs uppercase tracking-[0.18em] text-caption">Preview</p>
        <div className="grid grid-cols-4 gap-2 sm:grid-cols-8">
          {result.embedding_preview.map((value, index) => (
            <div
              key={`${value}-${index}`}
              className="rounded-sm border border-hairline bg-white px-2 py-3 text-center font-mono text-xs text-ink"
            >
              {value.toFixed(3)}
            </div>
          ))}
        </div>
      </div>
      {fullVector && (
        <div className="rounded-md border border-hairline bg-white p-5">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
            <p className="text-xs uppercase tracking-[0.18em] text-caption">
              Full vector
            </p>
            <div className="flex flex-wrap items-center gap-2">
              <p className="mr-2 font-mono text-xs text-caption">
                {fullVector.length} values
              </p>
              <button
                type="button"
                onClick={copyFullVector}
                className="inline-flex h-8 cursor-pointer items-center gap-2 rounded-md border border-hairline bg-white px-3 text-xs text-ink transition hover:-translate-y-px hover:shadow-soft"
              >
                {copied ? <Check size={13} /> : <Copy size={13} />}
                {copied ? "Copied" : "Copy"}
              </button>
              <button
                type="button"
                onClick={downloadFullVector}
                className="inline-flex h-8 cursor-pointer items-center gap-2 rounded-md border border-hairline bg-white px-3 text-xs text-ink transition hover:-translate-y-px hover:shadow-soft"
              >
                <Download size={13} />
                Download JSON
              </button>
            </div>
          </div>
          <textarea
            readOnly
            value={JSON.stringify(fullVector)}
            className="h-44 w-full resize-y rounded-md border border-hairline bg-[#F8F8F4] p-3 font-mono text-xs leading-5 text-ink outline-none"
          />
        </div>
      )}
    </section>
  );
}

function ProteinSummary({
  protein,
  status,
}: {
  protein: ResolvedProteinInput;
  status: string;
}) {
  return (
    <div className="rounded-md border border-hairline bg-white p-5">
      <div className="mb-2 flex items-center justify-between gap-3">
        <p className="truncate text-sm text-ink">{protein.accession ?? protein.source}</p>
        <CacheBadge status={status} />
      </div>
      <p className="text-sm text-muted">
        {protein.protein_name ?? protein.organism ?? "Resolved protein"}
      </p>
      <p className="mt-3 font-mono text-xs text-caption">
        {protein.sequence_length} aa
      </p>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-md border border-hairline bg-white p-6">
      <p className="text-xs uppercase tracking-[0.18em] text-caption">{label}</p>
      <p className="mt-4 truncate font-heading text-4xl font-medium tracking-tight text-ink">
        {value}
      </p>
    </div>
  );
}

function CacheBadge({ status }: { status?: string }) {
  if (!status) return null;

  const hit = status === "hit";
  return (
    <span className="inline-flex h-6 items-center gap-2 rounded-full border border-hairline bg-white px-3 text-[10px] uppercase tracking-[0.16em] text-muted">
      <span className={`size-1.5 rounded-full ${hit ? "bg-accent" : "bg-caption"}`} />
      {status}
    </span>
  );
}

function StatusPill({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof Activity;
  label: string;
  value: string;
}) {
  return (
    <div className="inline-flex h-8 max-w-full items-center gap-2 rounded-full border border-hairline bg-white px-3 text-xs">
      <Icon size={13} strokeWidth={1.5} className="shrink-0 text-caption" />
      <span className="text-caption">{label}</span>
      <span className="truncate text-ink">{value}</span>
    </div>
  );
}

function PrimaryButton({
  loading,
  label,
  icon: Icon,
  onClick,
}: {
  loading: boolean;
  label: string;
  icon: typeof Zap;
  onClick?: () => void;
}) {
  return (
    <button
      type={onClick ? "button" : "submit"}
      onClick={onClick}
      disabled={loading}
      className="inline-flex h-10 w-full cursor-pointer items-center justify-center gap-2 rounded-md bg-ink px-5 text-sm font-medium text-white transition hover:bg-ink-hover disabled:cursor-not-allowed disabled:opacity-50"
    >
      {loading ? <Loader2 size={15} className="animate-spin" /> : <Icon size={15} strokeWidth={1.5} />}
      {label}
    </button>
  );
}

function ErrorMessage({ message }: { message: string | null }) {
  if (!message) return null;

  return (
    <p className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
      {message}
    </p>
  );
}

function EmptyState() {
  return (
    <div className="grid min-h-48 place-items-center rounded-md border border-dashed border-hairline-strong bg-white p-8 text-center">
      <div>
        <Database className="mx-auto text-caption" size={20} strokeWidth={1.5} />
        <p className="mt-3 text-sm text-muted">No cached neighbors yet</p>
      </div>
    </div>
  );
}
