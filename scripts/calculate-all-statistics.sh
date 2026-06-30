set -e

./start-playwright-tests.sh
./generate-performance-summary.sh
./generate-plots.sh