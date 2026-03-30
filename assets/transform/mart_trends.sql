/* @bruin
name: threat_intelligence.mart_threat_trends
type: bq.sql
depends:
  - threat_intelligence.stg_urlhaus
  - threat_intelligence.stg_threatfox
materialization:
  type: table
  strategy: create+replace
@bruin */

WITH urlhaus_daily AS (
  SELECT
    DATE(dateadded) AS report_date,
    'urlhaus' AS source,
    threat AS threat_type,
    CAST(NULL AS STRING) AS malware_family,
    domain,
    tld,
    url_status,
    COUNT(*) AS daily_count
  FROM threat_intelligence.stg_urlhaus
  GROUP BY 1, 2, 3, 4, 5, 6, 7
),

threatfox_daily AS (
  SELECT
    DATE(first_seen_utc) AS report_date,
    'threatfox' AS source,
    threat_type,
    malware_family,
    CAST(NULL AS STRING) AS domain,
    CAST(NULL AS STRING) AS tld,
    CAST(NULL AS STRING) AS url_status,
    COUNT(*) AS daily_count
  FROM threat_intelligence.stg_threatfox
  GROUP BY 1, 2, 3, 4, 5, 6, 7
)

SELECT * FROM urlhaus_daily
UNION ALL
SELECT * FROM threatfox_daily
