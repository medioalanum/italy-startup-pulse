# Dashboard redesign reference

Visual reference: [Italy Pulse prototype](https://italypulse.vercel.app/)

The prototype is a visual and interaction reference only. Its sample values must not be copied into the production dashboard.

## Reusable implementation prompt

> Redesign the Italy Startup Pulse dashboard using the linked prototype as the visual reference: https://italypulse.vercel.app/
>
> Keep the existing FastAPI, Jinja2, SQLAlchemy, PostgreSQL, and Render architecture. Do not replace the backend or introduce a frontend framework for this iteration.
>
> Build a clear, responsive, single-page dashboard with these sections and anchor navigation:
>
> 1. **Overview:** show the selected registry snapshot, latest publication period, leading region, leading sector, and net change versus the previous comparable snapshot.
> 2. **Breakdowns:** allow the user to switch between Regions and Sectors. Display a ranked horizontal bar visualization and a detail table with rank, name, startup count, national share, and net change.
> 3. **Change over time:** show the available quarterly snapshots, identify the selected baseline, and explain when period-over-period movement cannot be calculated because there is no previous snapshot.
> 4. **Monitoring:** show the status of anomaly monitoring and clearly state when automated alerts are disabled because no approved detection rule exists.
> 5. **Methodology:** explain the aggregate data contract, independent region and sector dimensions, snapshot cadence, source attribution, and the meaning of net change.
>
> Use the real data contract: MIMIT reports provide aggregate totals by region and by economic sector in separate tables. Do not invent company-level records, new-entry counts, or region-by-sector cross-tabs. Support all available categories dynamically; never hardcode the two-region example from the prototype.
>
> Preserve the sample-data banner and distinguish sample data from live ingestion. Keep the interface in English, use accessible labels and table markup, and make the layout usable on mobile and desktop.
>
> Before editing, inspect the current templates, routes, database models, tests, and sample fixture. Implement the redesign incrementally, preserve existing endpoints unless a change is necessary, add meaningful tests for period selection and breakdown switching, run the full validation suite, and verify the rendered dashboard locally and on the demo deployment.

## Design decisions to preserve

- The prototype's hierarchy is more important than its exact colors or typography.
- Summary cards should answer what period is shown, how large the registry is, and what changed.
- Rankings should remain readable when all 20 regions or all 9 sectors are present.
- Methodology and source limitations must remain visible, not hidden in implementation notes.
- A missing previous snapshot must be presented as unavailable comparison data, not as a meaningful zero movement.
