// Upstream Dependency Blast Radius Query
// Parameters:
//   $service_name: string (e.g. "checkout-service")

MATCH path = (origin:Service {name: $service_name})-[:DEPENDS_ON*1..3]->(upstream:Service)
RETURN 
  origin.name AS incident_service,
  [s IN nodes(path) | s.name] AS dependency_chain,
  upstream.name AS upstream_dependency,
  upstream.status AS status;
