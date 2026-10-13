export type NodeType =
  | "Service"
  | "Repository"
  | "Commit"
  | "Developer"
  | "Deployment"
  | "Incident"
  | "RootCause"
  | "Fix";

export type RelationshipType =
  | "DEPENDS_ON"
  | "OWNED_BY"
  | "CHANGED_BY"
  | "DEPLOYED_BY"
  | "CAUSED_BY"
  | "RESOLVED_BY";

export interface ServiceNode {
  id: string;
  name: string;
  tier: "tier-0" | "tier-1" | "tier-2";
  language?: string;
  status: "healthy" | "degraded" | "outage";
}

export interface IncidentNode {
  id: string;
  title: string;
  severity: "P1" | "P2" | "P3" | "P4";
  status: "TRIGGERED" | "INVESTIGATING" | "RESOLVED";
  timestamp: number;
  error_message?: string;
}

export interface DeploymentNode {
  id: string;
  version: string;
  environment: string;
  timestamp: number;
  status: "SUCCESS" | "FAILED" | "ROLLED_BACK";
}

export interface CommitNode {
  sha: string;
  message: string;
  timestamp: number;
  diff_summary?: string;
}

export interface DeveloperNode {
  email: string;
  name: string;
  team: string;
  on_call: boolean;
}

export interface RootCauseNode {
  id: string;
  summary: string;
  category: string;
}

export interface FixNode {
  id: string;
  action_type: "ROLLBACK" | "RESTART" | "CONFIG_PATCH";
  description: string;
  command?: string;
}

export interface GraphEdge {
  id?: string;
  source: string;
  target: string;
  type: RelationshipType;
  properties?: Record<string, unknown>;
}

export interface GraphData {
  nodes: Array<{
    id: string;
    label: NodeType;
    properties: Record<string, unknown>;
  }>;
  edges: GraphEdge[];
}
