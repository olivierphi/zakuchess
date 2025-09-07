# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

**Primary development workflow:**
- `make dev` - Starts both FastAPI backend and Astro frontend in development mode
- `make install` - Install Python and Node.js dependencies

**Build and deployment:**
- `make prod` - Build frontend and start FastAPI in production mode
- `make frontend/build` - Build Astro frontend only

**Code quality:**
- `make code-quality/all` - Run all linting and type checking
- `make code-quality/frontend/oxlint` - Frontend linter
- `make code-quality/frontend/tsc` - TypeScript type checking
- `make code-quality/backend/ruff_format` - Python code formatting
- `make code-quality/backend/ruff_lint` - Python linting
- `make code-quality/backend/mypy` - Python type checking

**Individual services:**
- `make backend/dev` - FastAPI development server only
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

**Backend (FastAPI):**
- Located in `src-backend/zakuchess/`
- FastAPI serves as a proxy to Astro pages via `AstroPageProxyResponse`
- Environment-aware: serves static files in production, proxies to Astro dev server in development
- Python virtual environment managed by `uv`

**Frontend (Astro + React):**
- Located in `src-frontend/`
- Astro framework with React components for interactive UI
- TypeScript configuration uses `react-jsx` and separate type imports
- Chess game components in `src-frontend/components/chess/`
- TailwindCSS for styling

**Key Integration Points:**
- In development: FastAPI proxies requests to Astro dev server
- In production: FastAPI serves pre-built Astro static files
- Astro builds to `dist/` which FastAPI reads from in production mode
- Our own version of the game of chess follows the normal rules, but represents chess pieces
   with pixel arts characters - the assets for this are in the "public/assets/chess/units" folder.
- The chess "White" side is played by the "humans" units, in "public/assets/chess/units/humans".
    The chess "Black" side is played by the "undead" units, in "public/assets/chess/units/undead".

## Code Style

**Frontend:**
- TypeScript with strict configuration
- Oxlint enforces consistent type imports: `"fixStyle": "separate-type-imports"`
- React components use `.tsx` extension, Astro components use `.astro`

**Backend:**
- Python with Ruff for formatting and linting
- MyPy for type checking
- Pre-commit hooks installed via `make install`

## Requirements

- Node.js 22.x (enforced by Makefile)
- Python managed via `uv` (installed locally in `bin/`)
- Environment variables configured in `.env.local` (copy from `.env.dist`)
