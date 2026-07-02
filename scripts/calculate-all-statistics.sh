set -e

./start-playwright-tests.sh
./calculate-statistical-indicators.sh
./generate-plots.sh