output "dataset_id" {
  value = google_bigquery_dataset.threat_intelligence.dataset_id
}

output "bucket_name" {
  value = google_storage_bucket.raw_backup.name
}
