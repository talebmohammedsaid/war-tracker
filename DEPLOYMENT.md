# Deployment Guide

## 1) Deploy the Streamlit app on Render

1. Push this repository to GitHub.
2. Go to Render -> New + -> Blueprint.
3. Select your repository.
4. Render will detect `render.yaml` and create the service.
5. Wait for deploy to finish.
6. Copy your Render URL (example: `https://your-app.onrender.com`).

## 2) Point Vercel to your Streamlit URL

1. Open `vercel.json`.
2. Replace `https://YOUR-STREAMLIT-APP-URL` with your real Render URL.
3. Redeploy on Vercel.
4. Your Vercel domain will redirect to your Streamlit app.

## Notes

- Streamlit needs a persistent Python server, which is why Render is used.
- Vercel is used here as a frontend domain redirect.
