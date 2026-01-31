# Global Conference Atlas

A production-minded, single-page calendar for academic & research conferences.
It aggregates events from OpenAlex and Crossref via a backend proxy, normalizes
dates, and presents them in an accessible, elegant calendar + list UI.

## Features
- Month/week/day calendar with event cards (FullCalendar)
- List view with search and filters (topic, region, source, CFP deadline)
- Detail modal with source attribution, timezone-normalized dates, and metadata
- Admin panel for source status + last fetch times
- Background refresh, manual refresh, and cache-backed API proxy
- Mock mode so the frontend can run without the backend

## Repo Structure
- `src/` frontend React app
- `server/` Express API proxy + cache + normalization
- `server/tests/` unit tests for dedupe + date normalization
- `env.example` and `server/env.example` environment templates

## Quick Start

### 1) Frontend (mock mode)
```
npm install
cp env.example .env
npm run dev
```
Open `http://localhost:5173`.

### 2) Full stack (frontend + backend)
```
npm install
npm --prefix server install
cp env.example .env
cp server/env.example server/.env
npm run dev
```

### 3) Server tests
```
npm --prefix server run test
```

## Environment Variables

Frontend (`env.example`)
- `VITE_API_BASE`: base URL for API (ex: `http://localhost:5175`)
- `VITE_USE_MOCK`: set to `true` for mock data only

Backend (`server/env.example`)
- `PORT`: API port (default `5175`)
- `OPENALEX_EMAIL`: recommended for OpenAlex polite usage
- `CORS_ORIGIN`: comma-separated origins (ex: `http://localhost:5173`)
- `ADMIN_TOKEN`: optional token for `/api/admin/fetch-now`
- `ENABLE_BACKGROUND_FETCH`: `true`/`false`
- `REFRESH_INTERVAL_MINUTES`: background refresh interval

## API Endpoints
- `GET /api/events?from=YYYY-MM-DD&to=YYYY-MM-DD&source=openalex,crossref`
- `GET /api/event/:id`
- `GET /api/admin/status`
- `POST /api/admin/fetch-now` (send `x-admin-token` if configured)

## Common Event Schema
```
{
  id: string,
  title: string,
  description: string | null,
  start: ISODateString,
  end: ISODateString | null,
  timezone: string,
  source: "openalex" | "crossref" | "eventbrite" | "wikicfp",
  url: string,
  cfp_deadline: ISODateString | null,
  tags: string[],
  fetched_at: ISODateString
}
```

## Demo Script (3–4 steps)
1. Run `npm run dev` (full stack or mock mode).
2. Open the calendar and show the next 3 months filled with events.
3. Click any event to show the detail modal (source link + CFP deadline).
4. Open the Admin tab and show last fetch timestamps; hit Refresh.

## Notes
- OpenAlex + Crossref are enabled first for fast academic coverage.
- Eventbrite/WikiCFP can be added later in `server/src/sources/`.
- Respect source ToS and robots.txt for scraping sources.
# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```
