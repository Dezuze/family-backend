# Kollaparambil Family Application

A modern, private social platform and directory for the Kollaparambil family. This application features a rich interactive family tree, event management, news sharing, and a secure member directory.

## 🚀 Features

*   **Interactive Family Tree**: Visual D3.js powered force-directed graph to explore family connections.
*   **Member Directory**: Searchable directory of all family members with detailed profiles.
*   **News & Events**: Authenticated users can post news and schedule events.
*   **Calendar Integration**: "Add to Calendar" button for events (Google Calendar).
*   **Secure Access**: Invite-only registration system using unique Sponsor IDs.
*   **Media Gallery**: Photo sharing and gallery view.
*   **Committee Management**: View current committee members.
*   **Responsive Design**: Premium, mobile-first UI built with Nuxt 3 and Tailwind CSS.

## 🛠️ Tech Stack

*   **Frontend**: Nuxt 3 (Vue 3), Tailwind CSS, D3.js, Pinia.
*   **Backend**: Django REST Framework (Python), SQLite (Dev) / PostgreSQL (Prod ready).
*   **Infrastructure**: Docker, Docker Compose, Traefik (Reverse Proxy), Watchtower (Auto-updates).
*   **CI/CD**: GitHub Actions (Changes auto-pushed to GHCR).

## 📦 Getting Started

### Prerequisites
*   Docker & Docker Compose

### Running Locally
```bash
# Clone the repository
git clone https://github.com/Dezuze/family-backend.git
cd family-backend

# Start with Docker Compose
docker-compose up -d --build
```
The application will be available at:
*   **Frontend**: http://localhost
*   **Backend API**: http://localhost/api
*   **Traefik Dashboard**: http://localhost:8080

## 🔄 CI/CD & Deployment

This project uses **GitHub Actions** for Continuous Integration and Continuous Deployment.
1.  **Push to `main`**: Triggers the workflow.
2.  **Tests**: Backend tests are executed.
3.  **Build**: Docker images are built and pushed to GitHub Container Registry (`ghcr.io`).
4.  **Deploy**: `Watchtower` service on the server detects the new image and automatically restarts the application with the latest changes.

## 🛡️ License

Private - For Kollaparambil Family use only.
