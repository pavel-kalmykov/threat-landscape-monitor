/* @bruin
name: threat_intelligence.stg_urlhaus
type: bq.sql
depends:
  - threat_intelligence.raw_urlhaus_urls
materialization:
  type: table
  strategy: create+replace
@bruin */

SELECT
  CAST(id AS INT64) AS id,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%d %H:%M:%S', dateadded) AS dateadded,
  url,
  url_status,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%d %H:%M:%S', last_online) AS last_online,
  threat,
  tags,
  urlhaus_link,
  reporter,
  NET.HOST(url) AS domain,
  NET.PUBLIC_SUFFIX(url) AS tld,
  CASE
    WHEN url_status = 'offline'
      AND last_online IS NOT NULL
      AND dateadded IS NOT NULL
    THEN TIMESTAMP_DIFF(
      SAFE.PARSE_TIMESTAMP('%Y-%m-%d %H:%M:%S', last_online),
      SAFE.PARSE_TIMESTAMP('%Y-%m-%d %H:%M:%S', dateadded),
      SECOND
    )
  END AS takedown_seconds
FROM threat_intelligence.raw_urlhaus_urls
WHERE id IS NOT NULL
