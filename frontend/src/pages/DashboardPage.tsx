import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";

import {
  createBlog,
  disownBlog,
  fetchBlogs,
  fetchCollaborators,
  inviteCollaborator,
  revokeCollaborator,
  verifyBlog,
} from "../api/blogs";
import { useAuth } from "../hooks";
import type { BlogPayload, CollaboratorPayload } from "../types/api";

interface CreateFormState {
  naver_blog_id: string;
  title: string;
}

interface VerifyFormState {
  post_url: string;
  title: string;
  body: string;
}

export default function DashboardPage(): JSX.Element {
  const { session } = useAuth();
  const apiKey = session?.api_key ?? "";
  const [blogs, setBlogs] = useState<BlogPayload[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedBlogId, setSelectedBlogId] = useState<number | null>(null);

  const [createForm, setCreateForm] = useState<CreateFormState>({ naver_blog_id: "", title: "" });
  const [verifyForm, setVerifyForm] = useState<VerifyFormState>({ post_url: "", title: "", body: "" });
  const [collaborators, setCollaborators] = useState<CollaboratorPayload[]>([]);
  const [newCollaboratorEmail, setNewCollaboratorEmail] = useState("");

  const [actionMessage, setActionMessage] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [isBusy, setIsBusy] = useState(false);
  const [isLoadingCollaborators, setIsLoadingCollaborators] = useState(false);

  const loadBlogs = useCallback(async () => {
    if (!apiKey) {
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetchBlogs(apiKey);
      setBlogs(response);
      if (response.length > 0) {
        setSelectedBlogId((current) => current ?? response[0].id);
      } else {
        setSelectedBlogId(null);
      }
    } catch (err) {
      setError((err as Error).message || "Failed to load blogs");
    } finally {
      setIsLoading(false);
    }
  }, [apiKey]);

  useEffect(() => {
    if (apiKey) {
      void loadBlogs();
    }
  }, [apiKey, loadBlogs]);

  const selectedBlog = useMemo(
    () => blogs.find((blog) => blog.id === selectedBlogId) ?? null,
    [blogs, selectedBlogId]
  );

  useEffect(() => {
    setVerifyForm({ post_url: "", title: "", body: "" });
    setNewCollaboratorEmail("");
    setActionMessage(null);
    setActionError(null);
  }, [selectedBlogId]);

  useEffect(() => {
    if (!selectedBlogId || !apiKey) {
      setCollaborators([]);
      return;
    }
    setIsLoadingCollaborators(true);
    setActionError(null);
    setActionMessage(null);
    fetchCollaborators(apiKey, selectedBlogId)
      .then(setCollaborators)
      .catch((err) => setActionError((err as Error).message || "Failed to load collaborators"))
      .finally(() => setIsLoadingCollaborators(false));
  }, [apiKey, selectedBlogId]);

  const handleCreateBlog = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!apiKey) {
      return;
    }
    setIsBusy(true);
    setActionError(null);
    setActionMessage(null);
    try {
      const payload = await createBlog(apiKey, {
        naver_blog_id: createForm.naver_blog_id.trim(),
        title: createForm.title.trim() || undefined,
      });
      setCreateForm({ naver_blog_id: "", title: "" });
      setBlogs((current) => [payload, ...current]);
      setSelectedBlogId(payload.id);
      setActionMessage(`Blog ${payload.naver_blog_id} created. Drop the tokens into your verification post.`);
    } catch (err) {
      setActionError((err as Error).message || "Unable to create blog");
    } finally {
      setIsBusy(false);
    }
  };

  const handleVerifyBlog = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!apiKey || !selectedBlog) {
      return;
    }
    setIsBusy(true);
    setActionError(null);
    setActionMessage(null);
    try {
      await verifyBlog(apiKey, selectedBlog.id, {
        post_url: verifyForm.post_url.trim(),
        title: verifyForm.title.trim() || undefined,
        body: verifyForm.body.trim() || undefined,
      });
      setVerifyForm({ post_url: "", title: "", body: "" });
      await loadBlogs();
      setActionMessage("Verification check complete. Refresh to confirm status.");
    } catch (err) {
      setActionError((err as Error).message || "Verification failed");
    } finally {
      setIsBusy(false);
    }
  };

  const handleDisownBlog = async () => {
    if (!apiKey || !selectedBlog) {
      return;
    }
    setIsBusy(true);
    setActionError(null);
    setActionMessage(null);
    try {
      await disownBlog(apiKey, selectedBlog.id);
      await loadBlogs();
      setActionMessage("Blog marked as disowned. Tokens revoked and collaborators removed.");
    } catch (err) {
      setActionError((err as Error).message || "Unable to disown blog");
    } finally {
      setIsBusy(false);
    }
  };

  const handleInviteCollaborator = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!apiKey || !selectedBlog || !newCollaboratorEmail.trim()) {
      return;
    }
    setIsBusy(true);
    setActionError(null);
    setActionMessage(null);
    try {
      await inviteCollaborator(apiKey, selectedBlog.id, newCollaboratorEmail.trim());
      setNewCollaboratorEmail("");
      const updated = await fetchCollaborators(apiKey, selectedBlog.id);
      setCollaborators(updated);
      setActionMessage("Invitation sent.");
    } catch (err) {
      setActionError((err as Error).message || "Unable to invite collaborator");
    } finally {
      setIsBusy(false);
    }
  };

  const handleRevokeCollaborator = async (collaboratorId: number) => {
    if (!apiKey || !selectedBlog) {
      return;
    }
    setIsBusy(true);
    setActionError(null);
    setActionMessage(null);
    try {
      await revokeCollaborator(apiKey, selectedBlog.id, collaboratorId);
      const updated = await fetchCollaborators(apiKey, selectedBlog.id);
      setCollaborators(updated);
      setActionMessage("Collaborator revoked.");
    } catch (err) {
      setActionError((err as Error).message || "Unable to revoke collaborator");
    } finally {
      setIsBusy(false);
    }
  };

  return (
    <main className="dashboard">
      <div className="app-shell">
        <section className="card">
          <header className="section-header">
            <div>
              <h1>Blog workspaces</h1>
              <p>Connect owned Naver blogs, verify control, and manage the delivery team.</p>
            </div>
            <button className="btn secondary" type="button" onClick={() => void loadBlogs()} disabled={isLoading}>
              Refresh
            </button>
          </header>

          {error ? <p className="form-error">{error}</p> : null}
          {actionMessage ? <div className="toast success">{actionMessage}</div> : null}
          {actionError ? <div className="toast error">{actionError}</div> : null}

          <div className="dashboard-grid">
            <div className="dashboard-column">
              <form className="card sub" onSubmit={handleCreateBlog}>
                <h2>Create new blog</h2>
                <label htmlFor="naverId">Naver blog ID</label>
                <input
                  id="naverId"
                  value={createForm.naver_blog_id}
                  onChange={(event) => setCreateForm((state) => ({ ...state, naver_blog_id: event.target.value }))}
                  placeholder="clinic-care"
                  required
                  disabled={isBusy}
                />
                <label htmlFor="naverTitle">Display title (optional)</label>
                <input
                  id="naverTitle"
                  value={createForm.title}
                  onChange={(event) => setCreateForm((state) => ({ ...state, title: event.target.value }))}
                  placeholder="Seoul Clinic Blog"
                  disabled={isBusy}
                />
                <button type="submit" className="btn primary" disabled={isBusy}>
                  {isBusy ? "Saving…" : "Generate tokens"}
                </button>
              </form>

              <div className="card sub">
                <h2>Your blogs</h2>
                {isLoading ? (
                  <p>Loading blogs…</p>
                ) : blogs.length === 0 ? (
                  <p>No blogs yet. Create one to get verification tokens.</p>
                ) : (
                  <ul className="blog-list">
                    {blogs.map((blog) => (
                      <li key={blog.id}>
                        <button
                          type="button"
                          className={`blog-item${selectedBlogId === blog.id ? " active" : ""}`}
                          onClick={() => setSelectedBlogId(blog.id)}
                        >
                          <span>
                            <strong>{blog.title || blog.naver_blog_id}</strong>
                            <small>{blog.naver_blog_id}</small>
                          </span>
                          <span className={`status-chip ${blog.status}`}>
                            {blog.status === "pending" ? "Pending" : null}
                            {blog.status === "verified" ? "Verified" : null}
                            {blog.status === "disowned" ? "Disowned" : null}
                          </span>
                        </button>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>

            <div className="dashboard-column">
              {selectedBlog ? (
                <div className="card sub">
                  <h2>Verification tokens</h2>
                  <p className="muted">
                    Post the tokens below into a new Naver blog entry (title &amp; body). Hit verify once published.
                  </p>
                  <div className="token-block">
                    <span>Title token</span>
                    <code>{selectedBlog.title_token}</code>
                  </div>
                  <div className="token-block">
                    <span>Body token</span>
                    <code>{selectedBlog.body_token}</code>
                  </div>
                  {selectedBlog.verified_at ? (
                    <div className="verification-status success">
                      Verified on {new Date(selectedBlog.verified_at).toLocaleString()}
                    </div>
                  ) : (
                    <div className="verification-status pending">Not verified yet</div>
                  )}

                  <form className="verify-form" onSubmit={handleVerifyBlog}>
                    <label htmlFor="verifyUrl">Verification post URL</label>
                    <input
                      id="verifyUrl"
                      type="url"
                      value={verifyForm.post_url}
                      onChange={(event) => setVerifyForm((state) => ({ ...state, post_url: event.target.value }))}
                      placeholder="https://blog.naver.com/..."
                      required
                      disabled={isBusy}
                    />
                    <label htmlFor="verifyTitle">Fetched title (optional)</label>
                    <textarea
                      id="verifyTitle"
                      value={verifyForm.title}
                      onChange={(event) => setVerifyForm((state) => ({ ...state, title: event.target.value }))}
                      placeholder="Paste the title if copy/paste is easier"
                      rows={2}
                      disabled={isBusy}
                    />
                    <label htmlFor="verifyBody">Fetched body (optional)</label>
                    <textarea
                      id="verifyBody"
                      value={verifyForm.body}
                      onChange={(event) => setVerifyForm((state) => ({ ...state, body: event.target.value }))}
                      placeholder="Paste the body HTML/text to speed up verification"
                      rows={4}
                      disabled={isBusy}
                    />
                    <div className="verify-actions">
                      <button type="submit" className="btn primary" disabled={isBusy}>
                        {isBusy ? "Checking…" : "Run verification"}
                      </button>
                      <button type="button" className="btn danger" onClick={handleDisownBlog} disabled={isBusy}>
                        Disown blog
                      </button>
                    </div>
                  </form>
                </div>
              ) : (
                <div className="card sub">
                  <p>Select a blog to manage verification and collaborators.</p>
                </div>
              )}

              {selectedBlog ? (
                <div className="card sub">
                  <h2>Collaborators</h2>
                  <form className="collab-form" onSubmit={handleInviteCollaborator}>
                    <label htmlFor="collabEmail">Invite teammate</label>
                    <input
                      id="collabEmail"
                      type="email"
                      value={newCollaboratorEmail}
                      onChange={(event) => setNewCollaboratorEmail(event.target.value)}
                      placeholder="writer@clinic.com"
                      disabled={isBusy}
                      required
                    />
                    <button type="submit" className="btn secondary" disabled={isBusy}>
                      Invite
                    </button>
                  </form>

                  {isLoadingCollaborators ? (
                    <p>Loading collaborators…</p>
                  ) : collaborators.length === 0 ? (
                    <p>No collaborators invited yet.</p>
                  ) : (
                    <ul className="collaborator-list">
                      {collaborators.map((collaborator) => (
                        <li key={collaborator.id}>
                          <div>
                            <strong>{collaborator.email ?? "Pending email"}</strong>
                            <small>Status: {collaborator.status}</small>
                          </div>
                          <button
                            type="button"
                            className="btn danger"
                            onClick={() => handleRevokeCollaborator(collaborator.id)}
                            disabled={isBusy}
                          >
                            Revoke
                          </button>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              ) : null}
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}






