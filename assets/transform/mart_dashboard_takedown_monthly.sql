/* @bruin
name: threat_intelligence.mart_dashboard_takedown_monthly
type: bq.sql
depends:
  - threat_intelligence.mart_takedown_analysis
materialization:
  type: table
  strategy: create+replace
@bruin */

SELECT
  FORMAT_TIMESTAMP('%Y-%m', dateadded) AS month,
  AVG(takedown_hours) AS mean,
  APPROX_QUANTILES(takedown_hours, 2)[OFFSET(1)] AS median
FROM threat_intelligence.mart_takedown_analysis
GROUP BY 1
ORDER BY 1
