export type Project = {
  slug: string;
  title: string;
  layer: string;
  summary: string;
  problem: string;
  whatIBuilt: string[];
  stack: string[];
  metrics: { label: string; value: string }[];
  architecture: string;
  run: string[];
  recruiterTakeaway: string;
  repoPath: string;
  featured: boolean;
};

export const projects: Project[] = [
  {
    slug: "citibike-lakehouse",
    title: "Citi Bike lakehouse",
    layer: "Bronze → Silver → Gold",
    summary:
      "Polars medallion pipeline that lands raw Citi Bike trips as Parquet, types and cleans them, then publishes gold aggregates.",
    problem:
      "Trip files arrive as messy CSVs: mixed timestamps, duplicate ride IDs, impossible durations, and station names that drift. Downstream analytics cannot sit on that raw extract.",
    whatIBuilt: [
      "A CLI (`python -m pipeline run`) that writes bronze / silver / gold Parquet layers.",
      "Deterministic cleaning: parse timestamps, drop zero-duration and >24h rides, dedupe on ride_id.",
      "Gold tables for daily volume, station traffic, and member vs casual mix.",
      "A bundled sample so the repo runs offline without downloading gigabytes of TLC data.",
    ],
    stack: ["Python", "Polars", "Parquet", "CLI"],
    metrics: [
      { label: "Layers", value: "3" },
      { label: "Sample trips", value: "1,200" },
      { label: "Runtime", value: "<2s" },
    ],
    architecture:
      "Raw CSV → bronze Parquet (as-landed) → silver (typed, deduped, duration_sec) → gold (daily_trips, station_traffic, membership_mix).",
    run: [
      "cd projects/citibike-lakehouse",
      "python3 -m venv .venv && source .venv/bin/activate",
      "pip install -r requirements.txt",
      "python -m pipeline run",
    ],
    recruiterTakeaway:
      "Shows I can design a lakehouse path, not just a notebook: explicit layers, typed silver, and aggregates that a warehouse can consume.",
    repoPath: "projects/citibike-lakehouse",
    featured: true,
  },
  {
    slug: "citibike-dbt-warehouse",
    title: "dbt transit warehouse",
    layer: "Staging → dims → facts",
    summary:
      "dbt Core + DuckDB star schema on cleaned trips: date and station dimensions, a trip fact, tests, and generated docs.",
    problem:
      "Gold Parquet is still a file dump. Analysts need conformed dimensions, grain that is documented, and tests that fail the build when a key breaks.",
    whatIBuilt: [
      "Staging models that rename and cast silver trips into warehouse-friendly columns.",
      "dim_date, dim_station, and fct_trips with documented grain (one row per ride_id).",
      "Generic tests: unique, not_null, accepted_values on member_casual and rideable_type.",
      "dbt docs that explain sources, refs, and the star schema.",
    ],
    stack: ["dbt Core", "DuckDB", "SQL", "YAML tests"],
    metrics: [
      { label: "Models", value: "6" },
      { label: "Tests", value: "12+" },
      { label: "Grain", value: "ride_id" },
    ],
    architecture:
      "Silver Parquet (source) → stg_trips → dim_date + dim_station + fct_trips. Tests run on every build.",
    run: [
      "cd projects/citibike-dbt-warehouse",
      "python3 -m venv .venv && source .venv/bin/activate",
      "pip install duckdb",
      "python -m warehouse run",
    ],
    recruiterTakeaway:
      "This is the warehouse half of the story: dimensional modeling, dbt tests, and a database that is cheap to clone.",
    repoPath: "projects/citibike-dbt-warehouse",
    featured: true,
  },
  {
    slug: "pipeline-orchestration",
    title: "Pipeline orchestration",
    layer: "Ingest → transform → dbt → quality",
    summary:
      "A daily DAG that runs the lakehouse, warehouse, and quality gate in order. Airflow file for recruiters, local runner for a laptop.",
    problem:
      "Four scripts are not a platform. Order, failure, and a single command to replay the day are what production actually needs.",
    whatIBuilt: [
      "An Airflow DAG (`citibike_daily`) with task dependencies recruiters expect.",
      "A no-Docker `python -m orchestrator run` that executes the same graph on this machine.",
      "Optional docker-compose for people who want a real Airflow UI.",
      "Clear task logs and a non-zero exit if any stage fails.",
    ],
    stack: ["Airflow DAG", "Python", "Docker Compose", "Task graph"],
    metrics: [
      { label: "Tasks", value: "4" },
      { label: "Schedule", value: "@daily" },
      { label: "Docker", value: "optional" },
    ],
    architecture:
      "ingest_lakehouse → run_dbt → run_quality → publish_status. Downstream tasks skip if an upstream stage fails.",
    run: [
      "cd projects/pipeline-orchestration",
      "python3 -m venv .venv && source .venv/bin/activate",
      "pip install -r requirements.txt",
      "python -m orchestrator run",
    ],
    recruiterTakeaway:
      "Demonstrates orchestration thinking: explicit dependencies, a replayable daily job, and a laptop path that does not require a cluster.",
    repoPath: "projects/pipeline-orchestration",
    featured: true,
  },
  {
    slug: "data-quality-framework",
    title: "Data quality framework",
    layer: "Contracts → checks → report",
    summary:
      "JSON schema contracts plus row-count, null-rate, freshness, and referential checks that emit Markdown/HTML and fail in pytest.",
    problem:
      "A green dbt run is not the same as trustworthy data. Volume cliffs, stale files, and orphan station IDs still ship without a contract layer.",
    whatIBuilt: [
      "Versioned JSON contracts for silver trips and gold daily aggregates.",
      "Checks for row counts, null rates, freshness windows, and FK-style station integrity.",
      "A Markdown + HTML report written on every run.",
      "pytest so CI can fail the PR when a contract breaks.",
    ],
    stack: ["Python", "JSON Schema", "pytest", "HTML report"],
    metrics: [
      { label: "Contracts", value: "2" },
      { label: "Check types", value: "4" },
      { label: "pytest", value: "yes" },
    ],
    architecture:
      "Load tables → validate against contracts → run metric checks → write reports/quality_report.md + .html → exit 1 on fail.",
    run: [
      "cd projects/data-quality-framework",
      "python3 -m venv .venv && source .venv/bin/activate",
      "pip install -r requirements.txt",
      "python -m quality run && pytest",
    ],
    recruiterTakeaway:
      "Shows I treat quality as a product: contracts, measurable SLOs, a human-readable report, and tests in CI.",
    repoPath: "projects/data-quality-framework",
    featured: true,
  },
];

export function getProject(slug: string) {
  return projects.find((project) => project.slug === slug);
}
