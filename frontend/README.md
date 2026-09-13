# NatalIA web

React + TypeScript + Vite UI. Production assets are built into `../natalia/web` and served by FastAPI.

```bash
npm ci
npm run build
npm test
```

Development: start FastAPI on port 8000, then `npm run dev` (proxy `/api` to `http://127.0.0.1:8000`).
