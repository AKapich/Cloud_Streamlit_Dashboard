resource "google_project_service" "pubsub_googleapis_com" {
  project = "733094419233"
  service = "pubsub.googleapis.com"
}
# terraform import google_project_service.pubsub_googleapis_com 733094419233/pubsub.googleapis.com
