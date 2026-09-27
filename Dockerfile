FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN python -m spacy download en_core_web_sm

COPY . .

RUN mkdir -p data/raw data/database data/feature_store data/mlflow

EXPOSE 8000
EXPOSE 8501

CMD ["python", "-m", "serving.api"]