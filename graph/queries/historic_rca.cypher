// Historic Similar Incident & Proven Fix Matching Query
// Parameters:
//   $incident_id: string (e.g. "INC-4091")

MATCH (inc:Incident {id: $incident_id})-[:CAUSED_BY]->(s:Service)
MATCH (past:Incident)-[:CAUSED_BY]->(s)
WHERE past.id <> inc.id AND past.status = 'RESOLVED'
MATCH (past)-[:CAUSED_BY]->(rc:RootCause)
MATCH (past)-[:RESOLVED_BY]->(fix:Fix)
RETURN 
  past.id AS past_incident_id,
  past.title AS past_title,
  rc.category AS root_cause_category,
  rc.summary AS root_cause_summary,
  fix.action_type AS fix_type,
  fix.description AS fix_description,
  fix.command AS rollback_command
LIMIT 3;
