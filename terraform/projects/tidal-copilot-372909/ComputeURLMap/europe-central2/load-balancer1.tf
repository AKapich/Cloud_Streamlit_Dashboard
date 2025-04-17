resource "google_compute_region_url_map" "load_balancer1" {
  default_service = "https://www.googleapis.com/compute/v1/projects/tidal-copilot-372909/regions/europe-central2/backendServices/streamlit"
  name            = "load-balancer1"
  project         = "tidal-copilot-372909"
  region          = "europe-central2"
}
# terraform import google_compute_region_url_map.load_balancer1 projects/tidal-copilot-372909/regions/europe-central2/urlMaps/load-balancer1
