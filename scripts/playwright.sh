set -e

cd ../playwright-kanban
npm install
npx playwright test
