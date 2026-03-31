/* @bruin
name: threat_intelligence.mart_dashboard_stats
type: bq.sql
depends:
  - threat_intelligence.stg_urlhaus
  - threat_intelligence.stg_threatfox
  - threat_intelligence.mart_takedown_analysis
materialization:
  type: table
  strategy: create+replace
@bruin */

SELECT
  (SELECT COUNT(*) FROM threat_intelligence.stg_urlhaus) AS total_urls,
  (SELECT COUNT(*) FROM threat_intelligence.stg_urlhaus WHERE url_status = 'online') AS still_online,
  (SELECT AVG(takedown_hours) FROM threat_intelligence.mart_takedown_analysis) AS avg_takedown_h,
  (SELECT APPROX_QUANTILES(takedown_hours, 2)[OFFSET(1)] FROM threat_intelligence.mart_takedown_analysis) AS median_takedown_h,
  (SELECT COUNT(*) FROM threat_intelligence.stg_threatfox) AS total_iocs
