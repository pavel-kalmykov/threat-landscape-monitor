/* @bruin
name: threat_intelligence.mart_dashboard_domain_stats
type: bq.sql
depends:
  - threat_intelligence.mart_takedown_analysis
materialization:
  type: table
  strategy: create+replace
@bruin */

SELECT
  domain,
  AVG(takedown_hours) AS avg_hours,
  COUNT(*) AS url_count
FROM threat_intelligence.mart_takedown_analysis
GROUP BY 1
