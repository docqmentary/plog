# Deploying to Render

## Prerequisites
- Render account (https://render.com) with billing info if you plan to move beyond the free tier.
- Project repository pushed to GitHub, GitLab, or Bitbucket.
- Environment secrets ready: `OPENAI_API_KEY`, `NAVER_SEARCH_CLIENT_ID`, `NAVER_SEARCH_CLIENT_SECRET`, `NAVER_SEARCHAD_ACCESS_KEY`, `NAVER_SEARCHAD_SECRET_KEY`.

## One-time setup
1. Commit the new deployment files (`Dockerfile`, `.dockerignore`, `render.yaml`) and push the repository to your remote.
2. Sign in to Render and choose **New +**, then select **Web Service**.
3. Connect the repository that contains this project and select the branch you want to deploy.
4. Render detects the `render.yaml`; pick **Deploy** to create the service using the Docker build.
5. In the Render dashboard, open the service and use the **Environment** tab to add the required variables:
   - `ENVIRONMENT=production`
   - `OPENAI_API_KEY` (copy from your secrets manager)
   - `NAVER_SEARCH_CLIENT_ID`
   - `NAVER_SEARCH_CLIENT_SECRET`
   - `NAVER_SEARCHAD_ACCESS_KEY`
   - `NAVER_SEARCHAD_SECRET_KEY`
   - `DEV_ALLOW_HTTP_FETCH=false`
6. Trigger a deploy (Render automatically starts one after creation). Wait for the build to finish.

## Google OAuth callback URL
- Render assigns an HTTPS domain like `https://plog-api.onrender.com` once the service is live.
- In the Google Cloud console (`APIs & Services > Credentials`), edit your OAuth client and add the Render domain to the **Authorized domains** list.
- Set the client-side redirect URI (the frontend) to `https://<your-frontend-host>/oauth2/callback`, and make sure the frontend posts the resulting ID token to `https://plog-api.onrender.com/auth/google/callback`.
- The backend currently stubs Google token validation (`app/services/auth.py`); replace this with a real verification call before going live.

## Verification
- After the deploy succeeds, visit `https://<your-service>.onrender.com/healthz`. You should receive `{ "status": "ok" }`.
- The first request can take a few seconds because the container needs to warm up.
- Application data is stored in SQLite (`plog.db`) inside the container; this resets on each deploy. Migrate to a managed Postgres instance before production use.

## Next steps
- Share the Render service URL when applying for the Naver Search API key.
- If you later need background tasks or persistent storage, add a Render PostgreSQL instance and update `DATABASE_URL` in the environment variables.
## Frontend static site
- The `render.yaml` now includes a `plog-frontend` static service (root directory `frontend`).
- Render will run `npm install && npm run build` and publish the `frontend/dist` folder automatically.
- Set `VITE_API_BASE_URL` (defaults to the backend Render URL `https://plog-api.onrender.com`). Update this env var if the backend hostname changes.
- After pushing changes, both the backend and frontend redeploy automatically (or via **Manual Deploy** in the dashboard).
