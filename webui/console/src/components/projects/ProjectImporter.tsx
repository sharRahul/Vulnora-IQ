import { useCallback, useEffect, useRef, useState } from "react";
import { FolderUp, GitBranch, Loader2, RefreshCw, Trash2, FileCode2, HardDrive } from "lucide-react";
import { Button } from "@/components/ui/button";

/**
 * Projects — import and manage AI agent codebases for testing in the Agent Lab.
 *
 * Replaces the old `<iframe src="/agent-lab">`, which the app's own
 * `frame-ancestors 'none'` / `X-Frame-Options: DENY` headers always blocked (the
 * page rendered blank). This panel talks to the same `/api/agent-lab` endpoints
 * directly, so no self-framing is needed.
 */

interface AgentProject {
  id: string;
  source?: string;
  path?: string;
  file_count?: number;
  size_bytes?: number;
  framework?: string;
  has_dockerfile?: boolean;
  writable?: boolean;
}

interface AgentLabState {
  projects: AgentProject[];
  run_mode?: string;
}

async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(path, { credentials: "same-origin", ...options });
  if (!response.ok) throw new Error((await response.text()) || response.statusText);
  return response.json() as Promise<T>;
}

async function csrfToken(): Promise<string> {
  return (await api<{ csrf_token: string }>("/api/csrf-token")).csrf_token;
}

function postJson<T>(path: string, body: unknown, token: string): Promise<T> {
  return api<T>(path, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-CSRF-Token": token },
    body: JSON.stringify(body),
  });
}

function formatBytes(bytes?: number): string {
  if (!bytes || bytes <= 0) return "—";
  const units = ["B", "KB", "MB", "GB"];
  let value = bytes;
  let unit = 0;
  while (value >= 1024 && unit < units.length - 1) {
    value /= 1024;
    unit += 1;
  }
  return `${value.toFixed(value < 10 && unit > 0 ? 1 : 0)} ${units[unit]}`;
}

function sanitiseId(value: string): string {
  return value
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9._-]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 64);
}

export function ProjectImporter() {
  const [projects, setProjects] = useState<AgentProject[]>([]);
  const [runMode, setRunMode] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState<string>("");
  const [error, setError] = useState<string>("");
  const [notice, setNotice] = useState<string>("");
  const [gitUrl, setGitUrl] = useState("");
  const [gitBranch, setGitBranch] = useState("");
  const folderInputRef = useRef<HTMLInputElement>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const data = await api<AgentLabState>("/api/agent-lab");
      setProjects(data.projects || []);
      setRunMode(data.run_mode || "");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load projects.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const importFolder = useCallback(async (files: FileList) => {
    if (!files.length) return;
    setError("");
    setNotice("");
    setBusy("folder");
    try {
      const first = files[0] as File & { webkitRelativePath?: string };
      const topDir = (first.webkitRelativePath || first.name).split("/")[0];
      const projectId = sanitiseId(topDir) || `agent-${Date.now()}`;

      const { default: JSZip } = await import("jszip");
      const zip = new JSZip();
      let total = 0;
      for (const file of Array.from(files)) {
        const rel = (file as File & { webkitRelativePath?: string }).webkitRelativePath || file.name;
        // Root the archive at the project contents (drop the chosen folder's own
        // top-level name), and skip noise that bloats the upload.
        const inner = rel.split("/").slice(1).join("/") || file.name;
        if (/(^|\/)(\.git|node_modules|__pycache__|\.venv)(\/|$)/.test(rel)) continue;
        total += file.size;
        if (total > 48 * 1024 * 1024) throw new Error("Folder exceeds the 48 MB import limit. Remove build artifacts and retry.");
        zip.file(inner, file);
      }
      const base64 = await zip.generateAsync({ type: "base64", compression: "DEFLATE" });
      const token = await csrfToken();
      const result = await postJson<{ project_id: string }>(
        "/api/agent-lab/import/archive",
        { archive_base64: base64, project_id: projectId },
        token,
      );
      setNotice(`Imported “${result.project_id}” from folder.`);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Folder import failed.");
    } finally {
      setBusy("");
      if (folderInputRef.current) folderInputRef.current.value = "";
    }
  }, [refresh]);

  const importGit = useCallback(async () => {
    if (!gitUrl.trim()) return;
    setError("");
    setNotice("");
    setBusy("git");
    try {
      const token = await csrfToken();
      const result = await postJson<{ project_id: string }>(
        "/api/agent-lab/import/git",
        { url: gitUrl.trim(), branch: gitBranch.trim() || undefined },
        token,
      );
      setNotice(`Cloned “${result.project_id}” from Git.`);
      setGitUrl("");
      setGitBranch("");
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Git import failed.");
    } finally {
      setBusy("");
    }
  }, [gitUrl, gitBranch, refresh]);

  const removeProject = useCallback(async (id: string) => {
    setError("");
    setNotice("");
    setBusy(`del:${id}`);
    try {
      const token = await csrfToken();
      await postJson(`/api/agent-lab/projects/${encodeURIComponent(id)}/delete`, {}, token);
      setNotice(`Removed “${id}”.`);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not remove project.");
    } finally {
      setBusy("");
    }
  }, [refresh]);

  return (
    <section className="h-full overflow-y-auto p-4 scrollbar-thin sm:p-6">
      <div className="mx-auto max-w-5xl space-y-5">
        <header className="flex flex-wrap items-end justify-between gap-3">
          <div className="min-w-0">
            <p className="text-xs font-bold uppercase tracking-wide text-muted-foreground">Agent Lab</p>
            <h2 className="text-xl font-extrabold">Projects</h2>
            <p className="mt-1 text-sm text-muted-foreground">
              Import an AI agent codebase to analyse and deploy as a scan target.
              {runMode ? <span className="ml-1 text-xs">Run mode: <span className="font-semibold">{runMode}</span>.</span> : null}
            </p>
          </div>
          <Button size="sm" variant="ghost" onClick={() => void refresh()} disabled={loading}>
            <RefreshCw className={loading ? "size-4 animate-spin" : "size-4"} />
            <span>Refresh</span>
          </Button>
        </header>

        {error ? (
          <div className="rounded-lg border border-danger/40 bg-danger/10 px-3 py-2 text-sm text-danger">{error}</div>
        ) : null}
        {notice ? (
          <div className="rounded-lg border border-border bg-canvas px-3 py-2 text-sm text-muted-foreground">{notice}</div>
        ) : null}

        <div className="grid gap-4 md:grid-cols-2">
          {/* Import from a local folder — the primary path. */}
          <div className="rounded-xl border border-border bg-card p-4 shadow-card">
            <div className="mb-2 flex items-center gap-2">
              <FolderUp className="size-4 text-primary" />
              <h3 className="text-sm font-bold">Import from folder</h3>
            </div>
            <p className="mb-3 text-xs text-muted-foreground">
              Pick a folder containing your agent. It is packaged in your browser and uploaded — nothing leaves until you choose it.
            </p>
            <input
              ref={folderInputRef}
              type="file"
              // @ts-expect-error non-standard but widely supported folder-select attributes
              webkitdirectory=""
              directory=""
              multiple
              className="hidden"
              onChange={(e) => e.target.files && void importFolder(e.target.files)}
            />
            <Button
              variant="primary"
              size="sm"
              disabled={busy === "folder"}
              onClick={() => folderInputRef.current?.click()}
            >
              {busy === "folder" ? <Loader2 className="size-4 animate-spin" /> : <FolderUp className="size-4" />}
              <span>{busy === "folder" ? "Packaging…" : "Choose folder"}</span>
            </Button>
          </div>

          {/* Import from a Git repository. */}
          <div className="rounded-xl border border-border bg-card p-4 shadow-card">
            <div className="mb-2 flex items-center gap-2">
              <GitBranch className="size-4 text-primary" />
              <h3 className="text-sm font-bold">Import from Git</h3>
            </div>
            <div className="space-y-2">
              <input
                className="input text-sm font-mono"
                placeholder="https://github.com/org/agent.git"
                value={gitUrl}
                onChange={(e) => setGitUrl(e.target.value)}
              />
              <input
                className="input text-sm"
                placeholder="Branch (optional)"
                value={gitBranch}
                onChange={(e) => setGitBranch(e.target.value)}
              />
              <Button variant="outline" size="sm" disabled={busy === "git" || !gitUrl.trim()} onClick={() => void importGit()}>
                {busy === "git" ? <Loader2 className="size-4 animate-spin" /> : <GitBranch className="size-4" />}
                <span>{busy === "git" ? "Cloning…" : "Clone repository"}</span>
              </Button>
            </div>
          </div>
        </div>

        <div>
          <div className="mb-2 flex items-center justify-between">
            <h3 className="text-sm font-bold">Imported projects</h3>
            <span className="text-xs text-muted-foreground">{projects.length} total</span>
          </div>

          {loading ? (
            <p className="text-sm text-muted-foreground">Loading projects…</p>
          ) : projects.length === 0 ? (
            <div className="rounded-xl border border-dashed border-border bg-canvas p-8 text-center">
              <FolderUp className="mx-auto mb-2 size-6 text-muted-foreground" />
              <p className="text-sm font-semibold">No projects yet</p>
              <p className="mx-auto mt-1 max-w-sm text-xs text-muted-foreground">
                Import a folder or clone a Git repository above to start analysing an agent.
              </p>
            </div>
          ) : (
            <div className="grid gap-3 sm:grid-cols-2">
              {projects.map((project) => (
                <div key={project.id} className="flex flex-col gap-2 rounded-xl border border-border bg-card p-4 shadow-card">
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0">
                      <p className="break-anywhere font-semibold">{project.id}</p>
                      <p className="mt-0.5 text-xs text-muted-foreground">
                        {project.source || "managed"}{project.framework ? ` · ${project.framework}` : ""}{project.has_dockerfile ? " · Dockerfile" : ""}
                      </p>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      disabled={busy === `del:${project.id}` || project.writable === false}
                      onClick={() => void removeProject(project.id)}
                      title={project.writable === false ? "Read-only project" : "Remove project"}
                    >
                      {busy === `del:${project.id}` ? <Loader2 className="size-4 animate-spin" /> : <Trash2 className="size-4" />}
                    </Button>
                  </div>
                  <div className="flex flex-wrap gap-3 text-xs text-muted-foreground">
                    <span className="inline-flex items-center gap-1"><FileCode2 className="size-3.5" />{project.file_count ?? "—"} files</span>
                    <span className="inline-flex items-center gap-1"><HardDrive className="size-3.5" />{formatBytes(project.size_bytes)}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
