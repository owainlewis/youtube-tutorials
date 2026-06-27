output "job_name" {
  description = "Cloud Run Job name"
  value       = google_cloud_run_v2_job.job.name
}

output "job_service_account_email" {
  description = "Email of the Cloud Run Job service account"
  value       = google_service_account.job_sa.email
}

output "scheduler_service_account_email" {
  description = "Email of the Cloud Scheduler service account"
  value       = google_service_account.scheduler_sa.email
}

output "scheduler_job_name" {
  description = "Cloud Scheduler trigger job name"
  value       = google_cloud_scheduler_job.trigger.name
}

output "alert_policy_id" {
  description = "Monitoring alert policy resource ID"
  value       = google_monitoring_alert_policy.job_failures.id
}

output "dashboard_url" {
  description = "URL to the Cloud Monitoring dashboard (empty if disabled)"
  value       = var.enable_dashboard ? "https://console.cloud.google.com/monitoring/dashboards/builder/${replace(google_monitoring_dashboard.service_dashboard[0].id, "projects/${var.project_id}/dashboards/", "")}?project=${var.project_id}" : ""
}
