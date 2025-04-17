resource "google_project_service" "cloudtrace_googleapis_com" {
  project = "733094419233"
  service = "cloudtrace.googleapis.com"
}
# terraform import google_project_service.cloudtrace_googleapis_com 733094419233/cloudtrace.googleapis.com
