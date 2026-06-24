set -e

cd ../statistics-kanban/seaborn

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

python src/main.py