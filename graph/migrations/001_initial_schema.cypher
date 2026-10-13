// ============================================================
// FalkorDB Migration 001: GraphOps Initial Schema & Indexes
// ============================================================
// Verified for official FalkorDB OpenCypher index syntax:
// CREATE INDEX FOR (n:Label) ON (n.property);

// Range indexes for primary identifiers and lookups
CREATE INDEX FOR (s:Service) ON (s.name);
CREATE INDEX FOR (r:Repository) ON (r.name);
CREATE INDEX FOR (c:Commit) ON (c.sha);
CREATE INDEX FOR (d:Developer) ON (d.email);
CREATE INDEX FOR (dep:Deployment) ON (dep.id);
CREATE INDEX FOR (i:Incident) ON (i.id);
CREATE INDEX FOR (rc:RootCause) ON (rc.id);
CREATE INDEX FOR (f:Fix) ON (f.id);

// Additional lookup indexes for high-frequency SRE queries
CREATE INDEX FOR (s:Service) ON (s.status);
CREATE INDEX FOR (dep:Deployment) ON (dep.timestamp);
CREATE INDEX FOR (i:Incident) ON (i.timestamp);
CREATE INDEX FOR (i:Incident) ON (i.status);
