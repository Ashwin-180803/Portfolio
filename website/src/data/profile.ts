export const profile = {
  name: "Ashwin Gehlot",
  title: "Data Engineer",
  githubHandle: "Ashwin-180803",
  github: "https://github.com/Ashwin-180803",
  email: "your.email@example.com",
  linkedin: "https://linkedin.com/in/your-handle",
  location: "Your City, Country",
  headline: "I turn messy event streams into trusted tables.",
  summary:
    "Data engineer focused on batch pipelines, dimensional models, and data quality. I care about contracts, reproducible runs, and making gold tables that analysts can actually trust.",
  about: [
    "I build the unglamorous parts of analytics that have to work every day: ingest, typing, slowly changing dimensions, tests, and orchestration. The Citi Bike platform in this repo is a complete local example of how I think about that work.",
    "My default stack is Python, SQL, and warehouse tooling (dbt, DuckDB, Parquet). I would rather ship a pipeline you can clone and run than a slide deck of logos.",
    "Edit this file — src/data/profile.ts — to add your real email, LinkedIn, and location.",
  ],
  skills: [
    {
      group: "Languages",
      items: ["Python", "SQL", "TypeScript"],
    },
    {
      group: "Pipelines",
      items: ["Polars", "Parquet", "Medallion architecture", "Airflow DAGs"],
    },
    {
      group: "Warehouse",
      items: ["dbt Core", "DuckDB", "Star schema", "Incremental models"],
    },
    {
      group: "Quality",
      items: ["Schema contracts", "Freshness", "Referential checks", "pytest"],
    },
  ],
  otherWork: [
    {
      name: "Booking widget",
      description: "Calendly-style scheduling with Google Calendar and email confirmation.",
      href: "https://github.com/Ashwin-180803/Personal-Projects",
    },
    {
      name: "LAN recon CLI",
      description: "Python subnet discovery, banner grabs, and heuristic service warnings.",
      href: "https://github.com/Ashwin-180803/Personal-Projects",
    },
  ],
};
