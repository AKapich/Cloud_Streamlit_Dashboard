resource "google_compute_subnetwork" "proxy_subnet1" {
  ip_cidr_range              = "10.0.0.0/24"
  name                       = "proxy-subnet1"
  network                    = "https://www.googleapis.com/compute/v1/projects/tidal-copilot-372909/global/networks/default"
  private_ipv6_google_access = "DISABLE_GOOGLE_ACCESS"
  project                    = "tidal-copilot-372909"
  purpose                    = "REGIONAL_MANAGED_PROXY"
  region                     = "europe-central2"
  role                       = "ACTIVE"
}
# terraform import google_compute_subnetwork.proxy_subnet1 projects/tidal-copilot-372909/regions/europe-central2/subnetworks/proxy-subnet1
