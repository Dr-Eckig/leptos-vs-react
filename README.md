# Leptos vs. React: Comparison of Performance and Reactivity Using a Kanban Board

This repository contains two functionally comparable Kanban applications:

- `react-kanban`: implementation using React and TypeScript
- `leptos-kanban`: implementation using Leptos and Rust/WASM

The project also includes automated Playwright measurements and Python scripts
for the statistical analysis and visualization of the results.

## Prerequisites

The following software is required:

- Bash
- Node.js and npm
- Rust and Cargo
- Python 3 with the `venv` module
- `curl` for installing Qlty

The project-specific versions of Tokei, Qlty, and Trunk are defined in
`scripts/tool-versions.sh`. The scripts install these tools automatically in the
project-local `.tools/bin` directory. Node.js dependencies are installed using
the existing `package-lock.json` files.

All commands below must be run from the root directory of this repository.

## Starting the Applications

React and Leptos must be started in two separate terminals.

### 1. Start React

Run the following command in the first terminal:

```bash
./scripts/start-npm.sh
```

The script installs the locked npm dependencies, creates a production build,
and starts the application at:

```text
http://localhost:4173
```

### 2. Start Leptos

Run the following command in the second terminal:

```bash
./scripts/start-trunk.sh
```

The script installs the specified Trunk version, creates a release build, and
starts the application at:

```text
http://localhost:8080
```

The initial installation and compilation may take several minutes. Both servers
remain active until they are stopped with `Ctrl+C` in their respective
terminals.

## Running the Performance Measurements

Both applications must already be running. Then execute the following command
in a third terminal:

```bash
./scripts/playwright.sh
```

The script installs the Playwright version specified in the lockfile and the
corresponding browsers. It then runs the tests using Chromium, Firefox, and
WebKit. The raw data is stored in the following directories:

- `statistics-kanban/data`: performance measurements
- `statistics-kanban/dom-mutations-data`: DOM mutation measurements
- `statistics-kanban/bundle-size-data`: measured bundle sizes

If browser libraries are missing on a Linux system, they can be installed once
with system privileges:

```bash
cd playwright-kanban
npx --no-install playwright install --with-deps
cd ..
```

## Generating Charts and Tables

After the Playwright measurements have finished, run:

```bash
./scripts/generate-plots.sh
```

The script creates a Python virtual environment in `statistics-kanban/.venv`,
installs the exact dependencies specified in
`statistics-kanban/requirements.txt`, and generates the results in:

- `results/performance`
- `results/reactivity`
- `results/implementation`

## Generating Implementation Metrics

The static implementation metrics are generated separately:

```bash
./scripts/analyze-code.sh
```

This installs Tokei `14.0.0` and Qlty `0.640.0` locally within the project. The
generated reports are then available in `results/implementation`.

## Complete Workflow

![Workflow for starting the applications and running the tests and analyses](workflow.png)

```text
Terminal 1: ./scripts/start-npm.sh
Terminal 2: ./scripts/start-trunk.sh
Terminal 3: ./scripts/playwright.sh
            ./scripts/generate-plots.sh
            ./scripts/analyze-code.sh
```

Both servers must remain active throughout the Playwright measurements. They can
be stopped afterward with `Ctrl+C` in their respective terminals.

## Project Structure

```text
leptos-kanban/       Leptos/Rust implementation
leptos-book/         Leptos documentation used by the project
react-kanban/        React/TypeScript implementation
playwright-kanban/   automated browser and performance tests
statistics-kanban/   statistical analysis of the measurement data
shared/              shared assets and functions
scripts/             startup, measurement, and analysis scripts
results/             newly generated results
results-for-thesis/  results used in the bachelor's thesis
```
