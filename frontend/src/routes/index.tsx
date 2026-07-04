import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useMemo, useRef, useState } from "react";

export const Route = createFileRoute("/")({
  component: Mikata,
});

const API = "https://mikata-backend.onrender.com/api";

type Anime = {
  anime_id: number;
  name: string;
  genre: string;
  type: string;
  episodes: number;
  rating: number;
  poster?: string | null;
};

// Global poster cache
const posterCache = new Map<number, string | null>();

// Global queue — max 1 request per 350ms to respect Jikan's rate limit
const fetchQueue: (() => void)[] = [];
let queueRunning = false;

function processQueue() {
  if (fetchQueue.length === 0) { queueRunning = false; return; }
  queueRunning = true;
  const next = fetchQueue.shift()!;
  next();
  setTimeout(processQueue, 350);
}

function enqueueFetch(fn: () => void) {
  fetchQueue.push(fn);
  if (!queueRunning) processQueue();
}

async function fetchPoster(id: number): Promise<string | null> {
  if (posterCache.has(id)) return posterCache.get(id)!;
  return new Promise((resolve) => {
    enqueueFetch(async () => {
      try {
        const res = await fetch(`https://api.jikan.moe/v4/anime/${id}`);
        if (!res.ok) throw new Error("no");
        const j = await res.json();
        const url: string | null =
          j?.data?.images?.webp?.large_image_url ??
          j?.data?.images?.jpg?.large_image_url ??
          null;
        posterCache.set(id, url);
        resolve(url);
      } catch {
        posterCache.set(id, null);
        resolve(null);
      }
    });
  });
}

function AnimeCard({ anime, onClick, index }: { anime: Anime; onClick: () => void; index: number }) {
  const [poster, setPoster] = useState<string | null>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    // If poster already provided (trending), use it directly — no API call needed
    if (anime.poster) {
      setPoster(anime.poster);
      return;
    }
    let cancelled = false;
    fetchPoster(anime.anime_id).then((url) => {
      if (!cancelled) setPoster(url);
    });
    return () => { cancelled = true; };
  }, [anime.anime_id, anime.poster]);

  const genres = anime.genre?.split(",").map((g) => g.trim()).filter(Boolean) ?? [];

  return (
    <button
      onClick={onClick}
      className="group relative flex flex-col overflow-hidden rounded-lg bg-card text-left card-ring transition-all duration-500 hover:-translate-y-1.5 hover:card-ring-hover animate-fade-up"
      style={{ animationDelay: `${Math.min(index * 40, 500)}ms` }}
    >
      <span aria-hidden className="pointer-events-none absolute left-2 top-2 z-20 h-3 w-3 border-l border-t border-crimson-glow/70" />
      <span aria-hidden className="pointer-events-none absolute right-2 top-2 z-20 h-3 w-3 border-r border-t border-crimson-glow/0 group-hover:border-crimson-glow/70 transition-colors duration-500" />
      <span aria-hidden className="pointer-events-none absolute left-2 bottom-2 z-20 h-3 w-3 border-l border-b border-crimson-glow/0 group-hover:border-crimson-glow/70 transition-colors duration-500" />
      <span aria-hidden className="pointer-events-none absolute right-2 bottom-2 z-20 h-3 w-3 border-r border-b border-crimson-glow/70" />

      <div className="relative aspect-[2/3] w-full overflow-hidden bg-ink">
        {poster ? (
          <img
            src={poster}
            alt={anime.name}
            loading="lazy"
            onLoad={() => setLoaded(true)}
            className={`h-full w-full object-cover transition-all duration-[900ms] group-hover:scale-[1.08] ${
              loaded ? "opacity-100" : "opacity-0"
            }`}
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center bg-gradient-to-br from-ink via-secondary/60 to-ink">
            <span className="font-jp text-5xl text-crimson/30">味</span>
          </div>
        )}
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-ink via-ink/60 to-transparent" />
        <div
          className="pointer-events-none absolute inset-0 opacity-0 group-hover:opacity-30 transition-opacity duration-500"
          style={{ background: "linear-gradient(135deg, oklch(0.68 0.23 24 / 0.15), transparent 40%)" }}
        />

        <div className="absolute left-3 top-3 z-10 flex items-center gap-1 rounded-sm border border-crimson/30 bg-ink/85 px-2 py-1 backdrop-blur-md">
          <span className="text-[10px] leading-none text-crimson-glow">★</span>
          <span className="text-xs font-semibold tabular-nums leading-none">{anime.rating?.toFixed(2) ?? "—"}</span>
        </div>
        <div className="absolute right-3 top-3 z-10 seal px-2 py-1 text-[10px] uppercase tracking-widest">
          {anime.type || "TV"}
        </div>
        <div className="pointer-events-none absolute bottom-2 right-2 z-10 flex items-center gap-1 text-[9px] uppercase tracking-[0.3em] text-parchment/70">
          <span className="h-px w-6 bg-parchment/40" />
          <span className="font-jp">作品</span>
        </div>
      </div>

      <div className="relative flex flex-1 flex-col gap-2.5 p-4">
        <span className="absolute right-3 top-3 font-jp text-[10px] tracking-widest text-muted-foreground/60 tabular-nums">
          №{String(index + 1).padStart(3, "0")}
        </span>
        <h3 className="pr-10 font-display text-[15px] font-semibold leading-tight text-foreground line-clamp-2 group-hover:text-crimson-glow transition-colors duration-300">
          {anime.name}
        </h3>
        <div className="flex flex-wrap gap-1">
          {genres.slice(0, 2).map((g) => (
            <span
              key={g}
              className="rounded-sm border border-crimson/25 bg-crimson/10 px-1.5 py-0.5 text-[10px] font-medium uppercase tracking-wider text-crimson-glow"
            >
              {g}
            </span>
          ))}
        </div>
        <div className="mt-auto flex items-center justify-between border-t border-border/50 pt-2.5 text-xs text-muted-foreground">
          <span className="tabular-nums">
            {Number.isFinite(anime.episodes) && anime.episodes > 0 ? `${anime.episodes | 0} EP` : "—"}
          </span>
          <span className="font-jp text-crimson-glow/0 group-hover:text-crimson-glow transition-colors duration-300">
            見る →
          </span>
        </div>
      </div>
    </button>
  );
}

function Grid({ items, onPick }: { items: Anime[]; onPick: (a: Anime) => void }) {
  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
      {items.map((a, i) => (
        <AnimeCard key={a.anime_id} anime={a} index={i} onClick={() => onPick(a)} />
      ))}
    </div>
  );
}

function GridSkeleton({ count = 12 }: { count?: number }) {
  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="flex flex-col overflow-hidden rounded-lg bg-card card-ring">
          <div className="aspect-[2/3] w-full animate-pulse bg-gradient-to-br from-muted to-ink" />
          <div className="space-y-2 p-4">
            <div className="h-4 w-3/4 animate-pulse rounded bg-muted" />
            <div className="h-3 w-1/2 animate-pulse rounded bg-muted" />
          </div>
        </div>
      ))}
    </div>
  );
}

function Mikata() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Anime[]>([]);
  const [selected, setSelected] = useState<Anime | null>(null);
  const [recs, setRecs] = useState<Anime[]>([]);
  const [loadingSearch, setLoadingSearch] = useState(false);
  const [loadingRecs, setLoadingRecs] = useState(false);
  const [loadingFeatured, setLoadingFeatured] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [featured, setFeatured] = useState<Anime[]>([]);
  const recsRef = useRef<HTMLDivElement>(null);

  // Load trending from Jikan — images bundled in response, no extra calls
  useEffect(() => {
    (async () => {
      setLoadingFeatured(true);
      try {
        const res = await fetch(
          "https://api.jikan.moe/v4/top/anime?type=tv&filter=bypopularity&limit=18"
        );
        const j = await res.json();
        const list: Anime[] = (j.data ?? []).map((a: any) => ({
          anime_id: a.mal_id,
          name: a.title,
          genre: (a.genres ?? []).map((g: any) => g.name).join(", "),
          type: a.type ?? "TV",
          episodes: a.episodes ?? 0,
          rating: a.score ?? 0,
          poster: a.images?.webp?.large_image_url ?? a.images?.jpg?.large_image_url ?? null,
        }));
        setFeatured(list);
      } catch {
        // silent fail
      } finally {
        setLoadingFeatured(false);
      }
    })();
  }, []);

  const displayed = query.trim() ? results : featured;

  // Debounced search against Django backend
  useEffect(() => {
    const q = query.trim();
    if (!q) {
      setResults([]);
      setError(null);
      return;
    }
    const ctrl = new AbortController();
    const t = setTimeout(async () => {
      try {
        setLoadingSearch(true);
        setError(null);
        const res = await fetch(`${API}/search/?q=${encodeURIComponent(q)}`, { signal: ctrl.signal });
        const j = await res.json();
        setResults(j.results ?? []);
      } catch (e: unknown) {
        if ((e as { name?: string })?.name !== "AbortError") setError("Search failed. Try again.");
      } finally {
        setLoadingSearch(false);
      }
    }, 300);
    return () => {
      ctrl.abort();
      clearTimeout(t);
    };
  }, [query]);

  async function pick(a: Anime) {
    setSelected(a);
    setRecs([]);
    setLoadingRecs(true);
    setError(null);
    try {
      const res = await fetch(`${API}/recommend/?name=${encodeURIComponent(a.name)}`);
      const j = await res.json();
      setRecs(j.recommendations ?? []);
      setTimeout(() => recsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 50);
    } catch {
      setError("Could not load recommendations.");
    } finally {
      setLoadingRecs(false);
    }
  }

  const heading = useMemo(() => {
    if (query.trim()) return `Results for "${query.trim()}"`;
    return "Trending picks";
  }, [query]);

  const showingLoader = loadingSearch || (loadingFeatured && !query.trim());

  return (
    <div className="relative min-h-screen">
      {/* Fixed vertical tategaki rail */}
      <div className="pointer-events-none fixed left-3 top-1/2 z-10 hidden -translate-y-1/2 2xl:block">
        <div className="flex flex-col items-center gap-3">
          <div className="h-12 w-px bg-gradient-to-b from-transparent to-crimson/60" />
          <div className="tategaki font-jp text-[9px] font-medium tracking-[0.5em] text-crimson-glow/70">味方</div>
          <div className="h-12 w-px bg-gradient-to-b from-crimson/60 to-transparent" />
        </div>
      </div>

      {/* Header */}
      <header className="relative overflow-hidden">
        <div className="pointer-events-none absolute inset-0" aria-hidden>
          <div className="absolute -right-16 -top-24 select-none font-jp text-[26rem] font-black leading-none text-crimson/[0.055] animate-float-slow">
            味方
          </div>
          <div className="absolute right-1/3 top-40 select-none font-jp text-[8rem] font-black leading-none text-crimson/[0.04] rotate-[-8deg]">
            推
          </div>
        </div>
        <div className="absolute inset-x-0 top-0 h-[2px] bg-gradient-to-r from-transparent via-crimson to-transparent opacity-70" />

        <div className="relative mx-auto max-w-7xl px-6 pb-14 pt-10 sm:pt-16">
          {/* Brand bar */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="seal animate-seal h-11 w-11 rounded-md text-xl">味</div>
              <div>
                <div className="flex items-baseline gap-2">
                  <span className="font-display text-2xl font-bold tracking-tight">Mikata</span>
                  <span className="font-jp text-crimson-glow text-glow">味方</span>
                </div>
                <div className="text-[10px] uppercase tracking-[0.35em] text-muted-foreground">Your ally in anime</div>
              </div>
            </div>
            <div className="hidden items-center gap-3 sm:flex">
              <span className="font-jp text-xs tracking-[0.3em] text-muted-foreground">アニメ</span>
              <span className="h-4 w-px bg-border" />
              <span className="text-[10px] uppercase tracking-[0.3em] text-muted-foreground">est. 令和</span>
            </div>
          </div>

          {/* Hero */}
          <div className="mt-16 grid gap-10 md:grid-cols-[1.4fr_1fr] md:items-end">
            <div className="max-w-3xl">
              <div className="mb-5 flex items-center gap-3">
                <span className="h-px w-10 bg-crimson" />
                <span className="font-jp text-xs uppercase tracking-[0.4em] text-crimson-glow">第一話 · Chapter One</span>
              </div>
              <h1 className="font-display text-[2.75rem] font-bold leading-[1.05] sm:text-6xl md:text-[4.25rem]">
                Find your next{" "}
                <span className="relative inline-block">
                  <span className="text-crimson-glow text-glow">obsession</span>
                  <span className="absolute -bottom-1 left-0 right-0 h-[3px] bg-gradient-to-r from-transparent via-crimson to-transparent" />
                </span>
                .
              </h1>
              <p className="mt-6 max-w-xl text-base leading-relaxed text-muted-foreground">
                Search thousands of series and films. Tap any title to summon
                <span className="text-crimson-glow"> curated recommendations</span> — hand-picked for taste, not trends.
              </p>
            </div>
            <div className="relative hidden md:block">
              <div className="rounded-lg border border-crimson/20 bg-card/60 p-5 backdrop-blur-sm card-ring">
                <div className="font-jp text-[10px] uppercase tracking-[0.35em] text-crimson-glow">案内 · Guide</div>
                <p className="mt-3 font-display text-sm leading-relaxed text-foreground/90">
                  Type a title. Tap a poster. Discover a lineage of stories that share its soul.
                </p>
                <div className="mt-4 hairline-divider" />
                <div className="mt-4 flex items-center justify-between text-[10px] uppercase tracking-widest text-muted-foreground">
                  <span>Curated</span>
                  <span className="font-jp text-crimson-glow">·</span>
                  <span>Refined</span>
                  <span className="font-jp text-crimson-glow">·</span>
                  <span>Endless</span>
                </div>
              </div>
            </div>
          </div>

          {/* Search bar */}
          <div className="relative mt-10 max-w-2xl">
            <div className="absolute -inset-1 -z-10 rounded-2xl bg-gradient-to-r from-crimson/20 via-crimson-glow/25 to-crimson/20 blur-2xl" />
            <div className="flex items-center gap-3 rounded-xl border border-border bg-card/85 px-4 py-3.5 backdrop-blur-md transition-all duration-300 focus-within:border-crimson/60 focus-within:ring-2 focus-within:ring-crimson/30 focus-within:bg-card">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" className="shrink-0 text-crimson-glow">
                <circle cx="11" cy="11" r="7" stroke="currentColor" strokeWidth="2" />
                <path d="m20 20-3.5-3.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              </svg>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search — try 'Naruto', 'Steins;Gate', 'Frieren'…"
                className="flex-1 bg-transparent text-base text-foreground placeholder:text-muted-foreground focus:outline-none"
                autoFocus
              />
              <span className="hidden font-jp text-[10px] uppercase tracking-[0.3em] text-muted-foreground sm:inline">
                検索
              </span>
              {query && (
                <button
                  onClick={() => setQuery("")}
                  className="rounded-md border border-border/60 px-2 py-1 text-[10px] uppercase tracking-widest text-muted-foreground transition-colors hover:border-crimson/40 hover:bg-muted hover:text-foreground"
                >
                  clear
                </button>
              )}
            </div>
            {!query && (
              <div className="mt-4 flex flex-wrap items-center gap-2">
                <span className="text-[10px] uppercase tracking-[0.3em] text-muted-foreground">Try</span>
                {["Frieren", "Steins;Gate", "Vinland Saga", "Mushishi", "Monster"].map((s) => (
                  <button
                    key={s}
                    onClick={() => setQuery(s)}
                    className="rounded-full border border-border/60 bg-card/40 px-3 py-1 text-xs text-foreground/80 backdrop-blur transition-all hover:border-crimson/50 hover:bg-crimson/10 hover:text-crimson-glow"
                  >
                    {s}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
        <div className="hairline-divider mx-auto max-w-7xl opacity-60" />
      </header>

      {/* Main */}
      <main className="relative mx-auto max-w-7xl px-6 py-14">
        <div className="mb-8 flex items-end justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="h-px w-6 bg-crimson" />
              <span className="font-jp text-[10px] uppercase tracking-[0.4em] text-crimson-glow">検索 · Discover</span>
            </div>
            <h2 className="mt-2 font-display text-2xl font-bold sm:text-3xl">{heading}</h2>
          </div>
          {loadingSearch && (
            <span className="flex items-center gap-2 text-xs uppercase tracking-widest text-muted-foreground">
              <span className="inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-crimson-glow" />
              Searching
            </span>
          )}
        </div>

        {error && (
          <div className="mb-6 rounded-md border border-crimson/40 bg-crimson/10 p-4 text-sm text-crimson-glow">
            {error}
          </div>
        )}

        {showingLoader && displayed.length === 0 ? (
          <GridSkeleton count={12} />
        ) : displayed.length === 0 ? (
          <div className="rounded-lg border border-dashed border-border/70 p-16 text-center">
            <div className="mx-auto mb-3 font-jp text-4xl text-crimson/40">無</div>
            <p className="text-muted-foreground">No matches. Try another title.</p>
          </div>
        ) : (
          <Grid items={displayed} onPick={pick} />
        )}

        {/* Recommendations */}
        {(selected || loadingRecs) && (
          <section ref={recsRef} className="mt-24 scroll-mt-8">
            <div className="mb-10">
              <div className="hairline-divider" />
              <div className="mt-10 flex items-center gap-2">
                <span className="h-px w-6 bg-crimson" />
                <span className="font-jp text-[10px] uppercase tracking-[0.4em] text-crimson-glow">おすすめ · Recommendations</span>
              </div>
              <h2 className="mt-2 font-display text-2xl font-bold sm:text-3xl">
                Because you tapped{" "}
                <span className="text-crimson-glow text-glow">{selected?.name}</span>
              </h2>
              <p className="mt-2 max-w-xl text-sm text-muted-foreground">
                Similar in spirit, genre, and vibe — a lineage of stories that share its soul.
              </p>
            </div>
            {loadingRecs ? (
              <GridSkeleton count={10} />
            ) : recs.length > 0 ? (
              <Grid items={recs} onPick={pick} />
            ) : (
              <div className="rounded-lg border border-dashed border-border/70 p-12 text-center text-muted-foreground">
                No recommendations found.
              </div>
            )}
          </section>
        )}
      </main>

      {/* Footer */}
      <footer className="relative mx-auto mt-8 max-w-7xl px-6 py-10">
        <div className="hairline-divider mb-8 opacity-60" />
        <div className="flex flex-col items-center gap-3 text-center">
          <div className="seal h-10 w-10 rounded-md text-lg">味</div>
          <div className="font-jp text-xs uppercase tracking-[0.4em] text-muted-foreground">味方 · Mikata</div>
          <div className="text-[10px] uppercase tracking-widest text-muted-foreground/70">An ally for anime lovers</div>
        </div>
      </footer>
    </div>
  );
}