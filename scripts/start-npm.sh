set -e

cd ../react-kanban
npm install
npm run build
npm run preview -- --port 4173 --strictPort