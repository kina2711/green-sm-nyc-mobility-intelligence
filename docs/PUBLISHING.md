# Publishing to GitHub

## 1. Create the public repository

Create an empty public repository named `green-sm-nyc-mobility-intelligence` under the `kina2711` account. Do not initialize it with a README, `.gitignore`, or license because those files already exist locally.

## 2. Push the source code

Run from the project root:

```powershell
git add .
git commit -m "feat: publish NYC mobility intelligence portfolio"
git branch -M main
git remote add origin https://github.com/kina2711/green-sm-nyc-mobility-intelligence.git
git push -u origin main
```

The repository includes the aggregated real-data dashboard contracts. Raw TLC Parquet, DuckDB, virtual environments, caches, run artifacts, and credentials remain excluded by `.gitignore`.

## 3. Configure Actions permissions

In GitHub, open:

`Settings → Actions → General → Workflow permissions`

Select **Read and write permissions**, then save. This permission allows the CI metadata commit step to push changes on `main`. If branch protection is enabled, allow GitHub Actions to satisfy or bypass the relevant rule.

## 4. Enable GitHub Pages

Open:

`Settings → Pages → Build and deployment → Source`

Choose **GitHub Actions**. Then open the repository's **Actions** tab and run the `Deploy dashboard` workflow if it did not start automatically.

The expected public URL is:

`https://kina2711.github.io/green-sm-nyc-mobility-intelligence/`

## 5. Verify the release

- The `CI` workflow is green.
- The `Deploy dashboard` workflow is green.
- The public page shows `LOCAL DATA`, 2023–2025, and 843,752,700 raw rows.
- Browser developer tools show HTTP 200 for all six files under `dashboard/data/`.
- No raw Parquet, DuckDB, `.env`, token, or local path is present in the GitHub repository.

## Updating the public dashboard

After rebuilding the real-data pipeline locally, review the six aggregate JSON files and commit them:

```powershell
git add dashboard/data README.md
git commit -m "chore(data): publish refreshed dashboard snapshot"
git push
```

The Pages workflow redeploys whenever files under `dashboard/` change.
