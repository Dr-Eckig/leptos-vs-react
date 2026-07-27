# Running the Performance Workflow

This document explains how to run the performance measurement workflow for the Kanban comparison project.

The workflow uses several shell scripts. Some scripts start development or preview servers that keep running until they are stopped manually. Because of that, multiple terminal windows are required.

## 1. Make the scripts executable

Run the following commands once from the project `scripts` directory:

```bash
chmod +x generate-plots.sh
chmod +x start-npm.sh
chmod +x playwright.sh
chmod +x start-trunk.sh
```

This step only needs to be done once. After that, the scripts can be started directly from the terminal.

## 2. Start the React application

Open the first terminal window and run:

```bash
./scripts/start-npm.sh
```

This starts the React application, using the Vite preview server.

Keep this terminal open while running the tests. Do not close it until all Playwright tests are finished.

## 3. Start the Leptos application

Open a second terminal window and run:

```bash
./scripts/start-trunk.sh
```

This starts the Leptos application in release mode, using Trunk.

Keep this terminal open as well. The server needs to stay active while the Playwright tests are running.

## 4. Run the Playwright tests

Open a third terminal window and run:

```bash
./scripts/playwright.sh
```

This executes the automated Playwright tests against the running React and Leptos applications.
This can take some time.

The Chromium-only bundle-size test opens every application in a fresh browser context
and sums the response-body sizes of same-origin JavaScript, CSS, and WebAssembly
assets. Its raw measurements are written to
`statistics-kanban/bundle-size-data`. The remaining performance measurements
are stored below `statistics-kanban/data`; DOM observer measurements are stored
below `statistics-kanban/dom-mutations-data`.

Make sure that both application servers are already running before starting the tests.

## 5. Generate plots

After the Playwright tests have finished, run:

```bash
./scripts/generate-plots.sh
```

This generates performance plots and tables in `results/performance`. The
Chromium bundle-size bar chart is written to
`results/performance/bundle-size.png`. DOM observer plots and tables are written
to `results/reactivity`.

## 6. Generate implementation metrics

Run:

```bash
./scripts/analyze-code.sh
```

The cyclomatic-complexity reports and the table containing LOC, file count,
component count, and the remaining implementation metrics are written to
`results/implementation`.

## Terminal overview

The workflow requires at least three terminal windows:

```text
Terminal 1:
./start-npm.sh

Terminal 2:
./start-trunk.sh

Terminal 3:
./playwright.sh
./generate-plots.sh
```

## Stopping the servers

The React and Leptos servers keep running until they are stopped manually.

To stop a running server, go to the terminal where it is running and press:

```text
Ctrl + C
```

Do this for both the React server and the Leptos server after the tests are complete.

## Notes

- The scripts should be executed from the project root directory.
- The React and Leptos applications must both be running before the Playwright tests are started.
- The plot generation and summary generation should only be started after the Playwright tests have completed successfully.
