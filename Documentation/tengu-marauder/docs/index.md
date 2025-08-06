site_name: Tengu Marauder Vanguard
site_url: https://example.com
repo_url: https://github.com/ExMachinaParlor/Tengu-Marauder-Vanguard
theme:
  name: material
  features:
    - navigation.instant
    - navigation.sections
    - toc.integrate
    - content.code.annotate

nav:
  - Home: index.md
  - Getting Started:
      - Quick Start: getting-started/quickstart.md
      - Installation: getting-started/installation.md
      - Docker Setup: getting-started/docker-setup.md
  - Configuration:
      - Docker Compose: config/docker-compose.md
      - Reticulum: config/reticulum.md
      - TMV Config: config/tmv-config.md
      - Tools List: config/tools.md
      - Network Profiles: config/network-profiles.md
  - Usage:
      - Web UI: usage/web-ui.md
      - Flask App: usage/flask.md
      - ESP32 Marauder: usage/esp32-marauder.md
      - Reticulum Networking: usage/reticulum.md
  - Advanced:
      - Mesh Networking: advanced/mesh.md
      - Remote Ops: advanced/remote-access.md
  - About: about.md

markdown_extensions:
  - toc:
      permalink: true
  - admonition
  - codehilite
  - footnotes
  - pymdownx.superfences
  - pymdownx.details
