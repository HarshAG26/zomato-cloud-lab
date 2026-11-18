# Three-person, three-day contribution and GitHub plan

**Important:** GitHub records commit timestamps, but timestamps alone do not prove actual work. Make genuine incremental changes and push on the day they are completed. Do not fabricate/backdate commits. Only one member needs AWS permissions.

## One-time repository setup (Member A)

1. Create GitHub repository `zomato-cloud-lab` (private unless the instructor requests public). Add no auto-generated README or license if uploading this existing folder.
2. Extract project ZIP, open terminal in its root, run:
   ```bash
   git init
   git branch -M main
   git add .
   git commit -m "chore: initialize Zomato AWS lab scaffold"
   git remote add origin https://github.com/OWNER/zomato-cloud-lab.git
   git push -u origin main
   ```
3. GitHub repository > Settings > Collaborators > invite B and C by username. Require each member to accept.
4. Optionally protect `main` and require pull requests. Members work on separate branches; do not all edit `main` simultaneously.

## One-time setup (Members B and C)

```bash
git clone https://github.com/OWNER/zomato-cloud-lab.git
cd zomato-cloud-lab
git checkout -b feature/your-area
```

A uses `feature/aws-infrastructure`; B uses `feature/backend-frontend`; C uses `feature/testing-report`.

## Day 1: design and baseline

- **A — AWS architect:** review `docs/ARCHITECTURE.md`; validate template locally; commit `docs: define two-AZ and multi-region target design`.
- **B — application developer:** run local app, review API and UI, make one genuine UI or API improvement; commit `feat: implement restaurant listing and health endpoint` (only if that change is actually made).
- **C — testing and research:** add sourced Zomato/AWS references, case-study problem statement and measurement plan; commit `docs: add research sources and experiment plan`.

## Day 2: implementation and tests

- **A:** improve CloudFormation template or IAM/network review; regenerate template if app changes; commit `infra: configure ALB ASG and scaling policy`.
- **B:** improve order validation or tests and run tests; commit `test: cover API behavior`.
- **C:** improve load test, results CSV layout and chart script; commit `test: add bounded latency benchmark`.

## Day 3: validation, evidence, report

- **A:** **only authorized AWS operator** deploys short-lived stack with approval, captures ASG/ALB/CloudWatch evidence, deletes stack; commit `docs: record AWS deployment and cleanup evidence`.
- **B:** check ALB frontend/API behavior and document limitations; commit `docs: add application verification evidence`.
- **C:** run bounded load tests with A, fill real measured counts, plot real chart, add report and final results; commit `results: add measured latency and scaling chart`.

The messages above are examples; every commit must match actual changed files. All members should contribute at least one meaningful commit on each of the three days, for **at least nine genuine commits total**, plus PR merges. No fabricated screenshots, numbers or source citations.

## Daily Git workflow for each member

```bash
git checkout feature/your-area
git fetch origin
git merge origin/main
# edit only your assigned files
git status
git add path/to/your/changed/file
git commit -m "type: describe actual change"
git push -u origin feature/your-area
```

On GitHub: `Compare & pull request` > describe work/tests > request teammate review > merge into `main` after review. Then each member updates their branch:

```bash
git checkout feature/your-area
git fetch origin
git merge origin/main
```

If conflicts occur, resolve them together; do not force push `main`. For day-by-day attribution, save links to each member's commits and PRs in the final report. **Do not upload AWS secrets, `.pem`, `.env`, or credentials.**
