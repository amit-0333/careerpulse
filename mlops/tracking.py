import mlflow
import pickle
import pandas as pd
import os
from datetime import datetime
from river import naive_bayes, metrics, feature_extraction, compose
from model.online_learner import (
    prepare_training_data,
    build_text_for_river,
    assign_category,
    save_model,
)

MLFLOW_TRACKING_URI = "data/mlflow"
EXPERIMENT_NAME = "careerpulse_job_classifier"

def setup_mlflow():
    os.makedirs(MLFLOW_TRACKING_URI, exist_ok=True)
    mlflow.set_tracking_uri("sqlite:///data/mlflow/mlflow.db")
    mlflow.set_experiment(EXPERIMENT_NAME)
    print(f"[INFO] MLflow tracking uri: sqlite:///data/mlflow/mlflow.db")

def train_with_tracking(df):
    print("[INFO] Starting training with MLflow tracking...")
    setup_mlflow()
    with mlflow.start_run():
        model = compose.Pipeline(
            feature_extraction.BagOfWords(lowercase=True),
            naive_bayes.MultinomialNB()
        )
        metric = metrics.Accuracy()
        category_counts = df["category"].value_counts().to_dict()
        trained = 0
        for _, row in df.iterrows():
            text = build_text_for_river(row)
            label = row["category"]
            pred = model.predict_one(text)
            if pred is not None:
                metric.update(label, pred)
            model.learn_one(text, label)
            trained += 1
        accuracy = metric.get()
        mlflow.log_param("model_type", "MultinomialNB")
        mlflow.log_param("feature_type", "BagOfWords")
        mlflow.log_param("total_jobs", trained)
        mlflow.log_param("num_categories", len(category_counts))
        mlflow.log_param("training_date", datetime.now().isoformat())
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("total_jobs_trained", trained)
        for category, count in category_counts.items():
            mlflow.log_metric(f"category_{category}", count)
        save_model(model, metric)
        print(f"[SUCCESS] Accuracy: {accuracy:.2%}")
        print(f"[SUCCESS] Total jobs: {trained}")
        print(f"[INFO] Run logged to MLflow")
        return model, accuracy

def show_experiment_history():
    setup_mlflow()
    client = mlflow.tracking.MlflowClient()
    experiment = client.get_experiment_by_name(EXPERIMENT_NAME)
    if experiment is None:
        print("[WARNING] No experiments found yet")
        return
    runs = client.search_runs(experiment.experiment_id)
    print(f"[INFO] Total runs: {len(runs)}")
    for run in runs:
        print(f"  Run ID:   {run.info.run_id[:8]}...")
        print(f"  Accuracy: {run.data.metrics.get('accuracy', 0):.2%}")
        print(f"  Jobs:     {run.data.metrics.get('total_jobs_trained', 0)}")
        print(f"  Date:     {run.data.params.get('training_date', 'unknown')}")
        print()

if __name__ == "__main__":
    print(f"[INFO] MLflow Tracking Started: {datetime.now()}")
    df = prepare_training_data()
    model, accuracy = train_with_tracking(df)
    print(f"[INFO] Experiment history:")
    show_experiment_history()