variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for Cloud Run Job and Scheduler"
  type        = string
  default     = "europe-west1"
}

variable "service_name" {
  description = "Name of the Cloud Run Job (lowercase, hyphens). Used for SA names, scheduler, alerts."
  type        = string
}

variable "environment" {
  description = "prod / staging / dev"
  type        = string
  default     = "prod"
}

variable "image" {
  description = "Container image URI to run. Push to Artifact Registry first."
  type        = string
}

variable "schedule" {
  description = "Cron expression for Cloud Scheduler (e.g. '0 * * * *' for hourly)"
  type        = string
}

variable "timezone" {
  description = "Timezone for the scheduler"
  type        = string
  default     = "Etc/UTC"
}

variable "cpu" {
  description = "CPU limit for the job"
  type        = string
  default     = "1"
}

variable "memory" {
  description = "Memory limit for the job"
  type        = string
  default     = "512Mi"
}

variable "timeout_seconds" {
  description = "Job execution timeout in seconds (max 86400 / 24h)"
  type        = number
  default     = 600
}

variable "max_retries" {
  description = "Number of retry attempts on failure"
  type        = number
  default     = 1
}

variable "environment_variables" {
  description = "Env vars passed to the container at runtime"
  type        = map(string)
  default     = {}
}

variable "accessible_secrets" {
  description = "Secret Manager secret IDs the job's SA can access"
  type        = list(string)
  default     = []
}

variable "failure_threshold" {
  description = "Number of error logs in 5 min that trigger an alert"
  type        = number
  default     = 0
}

variable "notification_channel_ids" {
  description = "Cloud Monitoring notification channel resource IDs (e.g. projects/.../notificationChannels/...)"
  type        = list(string)
  default     = []
}

variable "enable_dashboard" {
  description = "Whether to create a Cloud Monitoring dashboard for this service"
  type        = bool
  default     = true
}
