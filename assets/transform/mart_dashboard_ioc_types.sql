/* @bruin
name: threat_intelligence.mart_dashboard_ioc_types
type: bq.sql
depends:
  - threat_intelligence.stg_threatfox
materialization:
  type: table
  strategy: create+replace
@bruin */

SELECT
  ioc_type,
  COUNT(*) AS count
FROM threat_intelligence.stg_threatfox
GROUP BY 1
ORDER BY 2 DESC
