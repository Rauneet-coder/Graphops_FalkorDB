// Causal Deployment and Commit Diff Query
// Parameters:
//   $incident_id: string (e.g. "INC-4091")

MATCH (inc:Incident {id: $incident_id})-[:CAUSED_BY]->(origin:Service)
MATCH (origin)-[:DEPENDS_ON*0..3]->(target:Service)
MATCH (dep:Deployment)-[:DEPLOYED_BY]->(target)
WHERE dep.timestamp <= inc.timestamp 
  AND dep.timestamp >= (inc.timestamp - 3600)
MATCH (dep)-[:DEPLOYED_BY]->(c:Commit)
MATCH (c)-[:CHANGED_BY]->(dev:Developer)
RETURN 
  target.name AS affected_service,
  dep.id AS deployment_id,
  dep.version AS version,
  dep.timestamp AS deployed_at,
  (inc.timestamp - dep.timestamp) AS seconds_before_incident,
  c.sha AS commit_sha,
  c.message AS commit_message,
  c.diff_summary AS diff_summary,
  dev.name AS author_name,
  dev.email AS author_email,
  dev.on_call AS is_on_call
ORDER BY dep.timestamp DESC
LIMIT 5;
