# MLDeck — End-to-End ML Platform 🎛️

![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![sklearn](https://img.shields.io/badge/sklearn-1.3%2B-orange) ![License](https://img.shields.io/badge/license-MIT-green) — End-to-End ML Platform 🎛️

A self-contained ML experiment platform. Upload datasets, run experiments, compare results, and manage models — all from a web dashboard. Shows that I can think about the full ML lifecycle, not just notebooks.

## Features

- **Experiment tracking** — log parameters, metrics, and metadata for every run
- **Model registry** — register, version, and tag models (staging, production)
- **Dataset management** — upload CSVs, view stats, select features
- **Run comparison** — side-by-side metric comparisons across experiments
- **Dashboard** — visual overview of all experiments and models
- **API access** — full REST API for programmatic use

## Getting Started

```bash
git clone https://github.com/YOUR_USERNAME/mldeck-platform.git
cd mldeck-platform

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt

python app.py
```

Open `http://localhost:8000`.

## Tech Stack

- **Backend:** Python, FastAPI
- **Data:** Pandas, NumPy, scikit-learn
- **Frontend:** HTML, CSS, JavaScript
- **Storage:** JSON file-based (no database required)

## Project Structure

```
mldeck-platform/
├── app.py              # FastAPI server
├── experiments.py      # Experiment tracking logic
├── models.py           # Model registry
├── requirements.txt
├── .env.example
├── static/
│   ├── index.html
│   ├── styles.css
│   └── script.js
└── README.md
```

## License

MIT


## Project Structure

```
mldeck-platform/
├── app.py           # FastAPI server and routes
├── experiments.py   # Experiment tracking engine
├── models.py        # Model registry and versioning
├── static/          # Frontend (HTML/CSS/JS)
├── tests/           # Test suite
├── Dockerfile
├── Makefile
└── requirements.txt
```

## Docker

```bash
docker build -t mldeck .
docker run -p 8000:8000 mldeck
```
