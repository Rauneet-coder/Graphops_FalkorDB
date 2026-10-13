export default function HomePage() {
  const nodes = [
    "Service",
    "Repository",
    "Commit",
    "Developer",
    "Deployment",
    "Incident",
    "RootCause",
    "Fix",
  ];

  const relationships = [
    "DEPENDS_ON",
    "OWNED_BY",
    "CHANGED_BY",
    "DEPLOYED_BY",
    "CAUSED_BY",
    "RESOLVED_BY",
  ];

  return (
    <main className="container">
      <header className="header">
        <div>
          <div className="logo-badge" style={{ marginBottom: "0.5rem" }}>
            ⚡ FalkorDB Hackathon
          </div>
          <h1>GraphOps</h1>
          <p style={{ color: "var(--text-secondary)", marginTop: "0.25rem" }}>
            AI-powered SRE Incident Investigation System
          </p>
        </div>
        <div className="status-pill">
          <span className="dot" />
          <span>FalkorDB Engine Ready</span>
        </div>
      </header>

      <section className="card-grid">
        <div className="card">
          <h2>Graph Ontology Nodes</h2>
          <p>
            Topology entities tracked within FalkorDB for rapid multi-hop
            traversal and causal correlation.
          </p>
          <div className="ontology-pill-list">
            {nodes.map((node) => (
              <span key={node} className="pill">
                :{node}
              </span>
            ))}
          </div>
        </div>

        <div className="card">
          <h2>Causal Relationships</h2>
          <p>
            Directional graph edges powering blast-radius analysis and root-cause
            deduction.
          </p>
          <div className="ontology-pill-list">
            {relationships.map((rel) => (
              <span
                key={rel}
                className="pill"
                style={{ borderColor: "rgba(255, 51, 102, 0.3)" }}
              >
                [{rel}]
              </span>
            ))}
          </div>
        </div>

        <div className="card">
          <h2>System Foundation</h2>
          <p>
            FastAPI asynchronous backend with native FalkorDB connectivity and
            Next.js frontend.
          </p>
          <div style={{ marginTop: "1rem" }}>
            <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
              Backend: <code>http://localhost:8000/health</code>
              <br />
              Graph DB: <code>FalkorDB (port 6379)</code>
            </p>
          </div>
        </div>
      </section>
    </main>
  );
}
