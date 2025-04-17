resource "google_project_service" "iam_googleapis_com" {
  project = "733094419233"
  service = "iam.googleapis.com"
}
# terraform import google_project_service.iam_googleapis_com 733094419233/iam.googleapis.com
