resource "google_project_service" "bigquery_googleapis_com" {
  project = "733094419233"
  service = "bigquery.googleapis.com"
}
# terraform import google_project_service.bigquery_googleapis_com 733094419233/bigquery.googleapis.com
