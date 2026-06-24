# Running the Performance Workflow

This document explains how to run the performance measurement workflow for the Kanban comparison project.

The workflow uses several shell scripts. Some scripts start development or preview servers that keep running until they are stopped manually. Because of that, multiple terminal windows are required.

## 1. Make the scripts executable

Run the following commands once from the project `scripts` directory:

```bash
chmod +x generate-performance-summary.sh
chmod +x generate-plots.sh
chmod +x start-npm.sh
chmod +x start-playwright-tests.sh
chmod +x start-trunk.sh
```

This step only needs to be done once. After that, the scripts can be started directly from the terminal.

## 2. Start the React application

Open the first terminal window and run:

```bash
./start-npm.sh
```

This starts the React application, for example using the Vite preview server.

Keep this terminal open while running the tests. Do not close it until all Playwright tests are finished.

## 3. Start the Leptos application

Open a second terminal window and run:

```bash
./start-trunk.sh
```

This starts the Leptos application using Trunk.

Keep this terminal open as well. The server needs to stay active while the Playwright tests are running.

## 4. Run the Playwright tests

Open a third terminal window and run:

```bash
./start-playwright-tests.sh
```

This executes the automated Playwright tests against the running React and Leptos applications.
This can take some time.

Make sure that both application servers are already running before starting the tests.

## 5. Generate plots

After the Playwright tests have finished, run:

```bash
./generate-plots.sh
```

This generates the plots from the collected performance data to `statistics-kanban/seaborn/plots`.

## 6. Generate the performance summary

Before or after the plots have been generated, run:

```bash
./generate-performance-summary.sh
```

This creates the final performance summary based on the test results.

## Terminal overview

The workflow requires at least three terminal windows:

```text
Terminal 1:
./start-npm.sh

Terminal 2:
./start-trunk.sh

Terminal 3:
./start-playwright-tests.sh
./generate-plots.sh
./generate-performance-summary.sh
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
