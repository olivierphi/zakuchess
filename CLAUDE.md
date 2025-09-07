# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

**Primary development workflow:**

- `make dev` - Starts both Hono backend and Astro frontend in development mode
- `make install` - Install frontend and Node.js dependencies

**Build and deployment:**

- `make prod` - Build frontend and start Hono in production mode
- `make frontend/build` - Build Astro frontend only

**Individual services:**

- `make backend/dev` - Hono development server only
- `make frontend/dev` - Astro development server only

## Goal of the project

The goal is to re-implement the previous version, which was almost feature-complete
but proved to be hard to maintain in the long run.

**A git worktree of the previous version can be found in the "worktrees/add-lichess-integration".**

- The tech stack there was based on Django, with HTMX to refresh the UI.
- HTML components were written using the Python package named "dominate".

**What we're trying to achieve here is a rewrite of the code in "worktrees/add-lichess-integration"**,
but with more focus on frontend technologies this time, as we rely on Astro and React islands.

## Architecture

This is a full-stack chess application with a hybrid architecture.

**Backend (Hono):**

- Located in `backend/`
- Hono serves as a proxy to Astro pages via `astro-bridge.ts`: it serves Astro static files in production, and proxies to Astro dev server in real tome in development

**Frontend (Astro + React):**

- Located in `frontend/`
- Astro framework with React components for interactive UI
- TypeScript configuration uses `react-jsx` and separate type imports
- Chess game components in `frontend/src/components/chess/`
- TailwindCSS for styling

**Code style:**

- React components should use named exports, rather than default ones
- When we import our own modules, we should use file extensions (`.ts` / `.tsx`)

**Key Integration Points:**

- In development: Hono proxies requests to Astro dev server
- In production: Hono serves pre-built Astro static files
- Astro builds to `dist/` which Hono reads from in production mode
- Our own version of the game of chess follows the normal rules, but represents chess pieces
  with pixel arts characters - the assets for this are in the "frontend/public/assets/chess/units" folder.
- The chess "White" side is played by the "humans" units, in "frontend/public/assets/chess/units/humans".
  The chess "Black" side is played by the "undead" units, in "frontend/public/assets/chess/units/undead".

## Code Style

- TypeScript with strict configuration
- Oxlint enforces consistent type imports: `"fixStyle": "separate-type-imports"`
- React components use `.tsx` extension, Astro components use `.astro`

## Requirements

- Node.js 24.x (enforced by Makefile)
- Environment variables configured in `.env.local` (copy from `.env.dist`)
