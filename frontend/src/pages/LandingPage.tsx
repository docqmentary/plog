import { Link } from "react-router-dom";

import { useAuth } from "../hooks";

const workflowCards = [
  {
    category: "Access",
    title: "Frictionless Google Sign-in",
    description: "Authenticate clinic staff in seconds and issue scoped API keys for connected tools.",
    items: [
      "Google OAuth with deterministic fallback for staging",
      "Session API returns clinic-scoped API key",
      "Audit-ready access trail for every collaborator",
    ],
  },
  {
    category: "Governance",
    title: "Naver Blog Ownership Checks",
    description: "Verify the right clinic owns the blog before automation starts publishing.",
    items: [
      "Two-token verification via title & body snippets",
      "Automated fetch job confirms tokens were posted",
      "Disown & collaborator management from a single view",
    ],
  },
  {
    category: "Discovery",
    title: "Keyword Intelligence",
    description: "Blend GPT ideation, Naver search volume, and saved insights from your own posts.",
    items: [
      "AI-generated draft keywords with fit score",
      "Monthly volume and PC/mobile split pulled from Naver",
      "Owned-post references surfaced for instant reuse",
    ],
  },
  {
    category: "Production",
    title: "Clinical Content Composer",
    description: "Outline, evidence calls, and ready-to-publish draft material in one flow.",
    items: [
      "Outline planner with evidence requests per section",
      "Compose with research streamlines clinical voice",
      "Image prompts plus final checklist and FAQ",
    ],
  },
];

const deliveryTimeline = [
  {
    title: "1. Connect clinic blog",
    detail: "Invite the marketing owner, drop verification tokens, and lock permissions per collaborator.",
  },
  {
    title: "2. Discover what to write",
    detail: "Start from doctor-provided draft or blank canvas—blend generated keywords with volume signals.",
  },
  {
    title: "3. Plan with evidence",
    detail: "Approve the AI outline, review required citations, and pull top 10 external references.",
  },
  {
    title: "4. Publish with confidence",
    detail: "Generate long-form draft, checklist, imagery prompts, and export-ready references.",
  },
];

const faqs = [
  {
    question: "Why is the product split into backend and frontend?",
    answer:
      "The backend already exposes the API flows—standing up a dedicated frontend lets the clinic team interact with those workflows without Postman or dashboards built for developers.",
  },
  {
    question: "Do I need credentials to test?",
    answer:
      "For staging you can use the deterministic dev user: just supply any email in the sign-in flow and Plog provisions a sandbox account automatically.",
  },
  {
    question: "How does deployment work on Render?",
    answer:
      "Backend stays as a Docker web service. This frontend ships as a Static Site (or Node service) pointing to the /frontend folder with build command 'npm run build'.",
  },
];

export default function LandingPage(): JSX.Element {
  const { session } = useAuth();
  const ctaTarget = session ? "/dashboard" : "/login";

  return (
    <main className="landing">
      <div className="app-shell">
        <section className="card hero">
          <span className="badge">Plog — Clinic Growth OS</span>
          <div>
            <h1>Plan, research, and publish clinic-grade blogs in hours, not weeks.</h1>
            <p>
              Plog lines up every step from Google login to medically reviewed blog drafts. Connect the clinic blog,
              pull live keyword intelligence, orchestrate citations, and deliver ready-to-post content packages.
            </p>
            <div className="hero-actions">
              <Link className="btn primary" to={ctaTarget}>
                {session ? "Open dashboard" : "Start now"}
              </Link>
              <Link className="btn secondary" to="/login">
                View auth flow
              </Link>
            </div>
          </div>
          <div className="grid cols-3">
            <div className="metric">
              <strong>30+</strong>
              <span>AI-assisted blog outlines every month</span>
            </div>
            <div className="metric">
              <strong>10x</strong>
              <span>Faster review loops with evidence requests attached</span>
            </div>
            <div className="metric">
              <strong>1</strong>
              <span>Workspace tying together doctors, writers, and marketers</span>
            </div>
          </div>
        </section>

        <section className="card" style={{ marginTop: "3rem" }}>
          <div className="section-title">Product pillars</div>
          <div className="grid cols-2">
            {workflowCards.map((card) => (
              <article key={card.title} className="card" style={{ boxShadow: "none", borderRadius: "14px" }}>
                <span className="tag">{card.category}</span>
                <h3 style={{ margin: "0.75rem 0 0.5rem", fontSize: "1.35rem" }}>{card.title}</h3>
                <p style={{ color: "#475569", marginTop: 0 }}>{card.description}</p>
                <ul className="list">
                  {card.items.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </article>
            ))}
          </div>
        </section>

        <section className="card" style={{ marginTop: "3rem" }}>
          <div className="section-title">End-to-end flow</div>
          <div className="grid cols-2">
            {deliveryTimeline.map((step) => (
              <article key={step.title} className="card" style={{ boxShadow: "none", borderRadius: "14px" }}>
                <h3 style={{ margin: 0, fontSize: "1.2rem" }}>{step.title}</h3>
                <p style={{ color: "#4b5563", marginTop: "0.5rem" }}>{step.detail}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="card" style={{ marginTop: "3rem" }}>
          <div className="section-title">Frequently asked</div>
          <div className="grid cols-1" style={{ gap: "1.5rem" }}>
            {faqs.map((faq) => (
              <article key={faq.question} className="card" style={{ boxShadow: "none", borderRadius: "14px" }}>
                <h3 style={{ margin: 0, fontSize: "1.15rem" }}>{faq.question}</h3>
                <p style={{ color: "#475569", marginTop: "0.65rem" }}>{faq.answer}</p>
              </article>
            ))}
          </div>
        </section>

        <footer className="footer">
          Built on FastAPI + Render + Vite. Next up: wire the flows above to real API calls in dedicated views.
        </footer>
      </div>
    </main>
  );
}
