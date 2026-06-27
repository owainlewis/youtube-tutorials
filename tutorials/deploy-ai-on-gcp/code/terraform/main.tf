# Reference Terraform module for a scheduled AI Cloud Run Job.
# Creates: Cloud Run Job, Cloud Scheduler trigger, service accounts, IAM bindings,
# log-based metric, alerting policy.
#
# Adapt to your project. The defaults reflect a small AI automation; tune
# resources, schedule, and alerting thresholds to match your workload.

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# --- APIs ---

resource "google_project_service" "required_apis" {
  for_each = toset([
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "cloudscheduler.googleapis.com",
    "secretmanager.googleapis.com",
    "aiplatform.googleapis.com",
    "firestore.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com",
  ])

  project = var.project_id
  service = each.value

  disable_on_destroy = false
}

# --- Service accounts ---

resource "google_service_account" "job_sa" {
  account_id   = "${var.service_name}-sa"
  display_name = "${var.service_name} Cloud Run Job"
  project      = var.project_id
}

resource "google_service_account" "scheduler_sa" {
  account_id   = "${var.service_name}-scheduler-sa"
  display_name = "${var.service_name} Scheduler"
  project      = var.project_id
}

# --- IAM bindings (minimal scope) ---

resource "google_project_iam_member" "job_vertex_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.job_sa.email}"
}

resource "google_project_iam_member" "job_firestore" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.job_sa.email}"
}

resource "google_secret_manager_secret_iam_member" "job_secret_access" {
  for_each = toset(var.accessible_secrets)

  project   = var.project_id
  secret_id = each.value
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.job_sa.email}"
}

resource "google_cloud_run_v2_job_iam_member" "scheduler_invoker" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_job.job.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.scheduler_sa.email}"
}

# --- Cloud Run Job ---

resource "google_cloud_run_v2_job" "job" {
  name     = var.service_name
  location = var.region
  project  = var.project_id

  labels = {
    service     = var.service_name
    environment = var.environment
  }

  template {
    template {
      service_account = google_service_account.job_sa.email
      timeout         = "${var.timeout_seconds}s"
      max_retries     = var.max_retries

      containers {
        image = var.image

        resources {
          limits = {
            cpu    = var.cpu
            memory = var.memory
          }
        }

        dynamic "env" {
          for_each = var.environment_variables
          content {
            name  = env.key
            value = env.value
          }
        }
      }
    }
  }

  depends_on = [google_project_service.required_apis]
}

# --- Cloud Scheduler ---

resource "google_cloud_scheduler_job" "trigger" {
  name             = "${var.service_name}-trigger"
  description      = "Triggers ${var.service_name} on schedule"
  schedule         = var.schedule
  time_zone        = var.timezone
  region           = var.region
  project          = var.project_id
  attempt_deadline = "320s"

  http_target {
    http_method = "POST"
    uri         = "https://${var.region}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.project_id}/jobs/${google_cloud_run_v2_job.job.name}:run"

    oauth_token {
      service_account_email = google_service_account.scheduler_sa.email
    }
  }

  depends_on = [google_project_service.required_apis]
}

# --- Monitoring ---

resource "google_monitoring_dashboard" "service_dashboard" {
  count   = var.enable_dashboard ? 1 : 0
  project = var.project_id

  dashboard_json = templatefile("${path.module}/dashboard.json.tftpl", {
    service_name = var.service_name
  })

  depends_on = [
    google_project_service.required_apis,
    google_logging_metric.failure_count,
  ]
}

resource "google_logging_metric" "failure_count" {
  name    = "${var.service_name}-failures"
  filter  = "resource.type=\"cloud_run_job\" AND resource.labels.job_name=\"${google_cloud_run_v2_job.job.name}\" AND severity>=ERROR"
  project = var.project_id

  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
  }
}

resource "google_monitoring_alert_policy" "job_failures" {
  display_name = "${var.service_name} failures"
  project      = var.project_id
  combiner     = "OR"

  conditions {
    display_name = "Job error log entries"

    condition_threshold {
      filter          = "resource.type=\"cloud_run_job\" AND resource.labels.job_name=\"${google_cloud_run_v2_job.job.name}\" AND metric.type=\"logging.googleapis.com/user/${google_logging_metric.failure_count.name}\""
      duration        = "0s"
      comparison      = "COMPARISON_GT"
      threshold_value = var.failure_threshold

      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_SUM"
      }
    }
  }

  notification_channels = var.notification_channel_ids

  documentation {
    content   = "Cloud Run Job ${var.service_name} reported errors. Check Cloud Logging for details."
    mime_type = "text/markdown"
  }
}
