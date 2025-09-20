# Plog Frontend

This folder contains the web client for Plog. It handles user authentication and the initial blog-management dashboard that talks to the FastAPI backend.

## Features
- Development login shortcut that exchanges an email for a Plog session via `/auth/google/callback`
- Protected dashboard listing owned blogs, surfacing verification tokens, and managing collaborators
- Inline actions to create blogs, run verification checks, disown blogs, and invite/revoke collaborators

## Prerequisites
- Node.js 18+
- npm 9+

## Getting started
1. Install dependencies:
   ```bash
   npm install
   ```
2. Copy the example environment file and adjust the API base if needed:
   ```bash
   cp .env.example .env
   ```
   Set `VITE_API_BASE_URL` to your backend URL (defaults to `http://localhost:8000`).
3. Run the local dev server:
   ```bash
   npm run dev
   ```
   Vite serves the site on http://localhost:5173/ by default. Use the login form to sign in with a dev email (no Google OAuth wiring required yet).

## Build
```bash
npm run build
```
The static assets are emitted to `dist/`.

## Deploying on Render
- **Type:** Static Site (or Node web service if you need server-side rendering later)
- **Root directory:** `frontend`
- **Build command:** `npm install && npm run build`
- **Publish directory:** `dist`
- **Environment variables:** set `VITE_API_BASE_URL` to your FastAPI URL (for example `https://plog-api.onrender.com`).

Because CORS is already open on the backend, the static frontend can call the APIs directly once `VITE_API_BASE_URL` is configured.
