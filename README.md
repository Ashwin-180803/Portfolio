# Ashwin Gehlot — Data Engineer portfolio

Personal site plus four local-first Citi Bike projects. Live site: **https://Ashwin-180803.github.io/Portfolio/**

Repo: [Ashwin-180803/Portfolio](https://github.com/Ashwin-180803/Portfolio)

## Layout

```
Portfolio/
  website/                 Astro + Tailwind site
  projects/
    citibike-lakehouse/    Polars medallion pipeline
    citibike-dbt-warehouse dbt-style star schema on DuckDB
    pipeline-orchestration Airflow DAG + laptop runner
    data-quality-framework Contracts, checks, pytest
  github-profile/          Copy into repo Ashwin-180803
```

Edit contact details in [`website/src/data/profile.ts`](website/src/data/profile.ts) (`email`, `linkedin`, `location`).

## Preview the site

```bash
cd website
npm install
npm run dev
```

The dev server uses the GitHub Pages base path, so open **http://localhost:4321/Portfolio/**.

Build:

```bash
cd website
npm run build
```

## Run the data platform

Each project has its own README. End-to-end:

```bash
# 1. lakehouse
cd projects/citibike-lakehouse
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m pipeline run

# 2. warehouse
cd ../citibike-dbt-warehouse
python3 -m venv .venv && source .venv/bin/activate
pip install duckdb
python -m warehouse run

# 3. quality
cd ../data-quality-framework
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m quality run
pytest

# 4. or replay the whole DAG
cd ../pipeline-orchestration
python3 -m orchestrator run
```

## GitHub Pages

This repo deploys with GitHub Actions ([`.github/workflows/deploy.yml`](.github/workflows/deploy.yml)). In the repo: **Settings → Pages → Source: GitHub Actions**. After the first successful workflow, the site is at https://Ashwin-180803.github.io/Portfolio/.

## GitHub profile README

Copy [`github-profile/README.md`](github-profile/README.md) into a repository named `Ashwin-180803` (the same as your GitHub username). GitHub will render it on https://github.com/Ashwin-180803.
