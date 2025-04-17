variable "project_id" {
  description = "ID projektu w GCP"
  type        = string
}

variable "region" {
  description = "Region GCP"
  type        = string
  default     = "europe-central2" # np. Warszawa
}

variable "credentials_file" {
  description = "Ścieżka do pliku JSON z kluczem service account"
  type        = string
}