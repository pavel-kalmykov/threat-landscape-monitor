/* @bruin
name: threat_intelligence.mart_takedown_analysis
type: bq.sql
depends:
  - threat_intelligence.stg_urlhaus
materialization:
  type: table
  strategy: create+replace
@bruin */

SELECT
  id,
  dateadded,
  url,
  domain,
  tld,
  url_status,
  last_online,
  threat,
  tags,
  reporter,
  takedown_seconds,
  ROUND(takedown_seconds / 3600.0, 2) AS takedown_hours,
  ROUND(takedown_seconds / 86400.0, 2) AS takedown_days,
  DATE(dateadded) AS report_date,
  EXTRACT(YEAR FROM dateadded) AS report_year,
  EXTRACT(MONTH FROM dateadded) AS report_month
FROM threat_intelligence.stg_urlhaus
WHERE takedown_seconds IS NOT NULL
  AND takedown_seconds > 0
