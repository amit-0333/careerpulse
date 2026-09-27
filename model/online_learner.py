import pickle
import os
import pandas as pd
from river import naive_bayes, metrics, stream, preprocessing, feature_extraction, compose
from datetime import datetime

MODEL_PATH = "data/feature_store/river_model.pkl"
METRICS_PATH = "data/feature_store/model_metrics.pkl"

CATEGORY_KEYWORDS = {
    "data_science": [
        "data scientist", "data science", "machine learning",
        "deep learning", "nlp", "ai engineer", "research scientist"
    ],
    "data_engineering": [
        "data engineer", "etl", "data platform", "big data",
        "spark engineer", "hadoop", "airflow", "data architect"
    ],
    "software_engineering": [
        "software engineer", "software developer", "backend",
        "frontend", "fullstack", "python developer", "java developer",
        "javascript developer", "web developer", "mobile developer"
    ],
    "devops_cloud": [
        "devops", "cloud engineer", "platform engineer",
        "site reliability", "infrastructure", "kubernetes", "docker"
    ],
    "data_analytics": [
        "data analyst", "business intelligence", "bi analyst",
        "bi developer", "analytics engineer", "reporting analyst"
    ],
    "product_management": [
        "product manager", "technical product manager",
        "senior product manager", "staff product manager"
    ],
    "security": [
        "cybersecurity", "security engineer", "security analyst",
        "penetration tester", "information security"
    ],
    "qa_testing": [
        "qa engineer", "quality assurance", "test engineer",
        "automation engineer", "sdet"
    ]
}
def assign_category(title):
    title_lower = title.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in title_lower:
                return category
    return "other_tech"

def prepare_training_data():
    print("[INFO] Loading features for training...")
    df = pd.read_csv("data/feature_store/jobs_features.csv")
    df = df.copy()
    df["category"] = df["title"].apply(assign_category)
    print(f"[INFO] Category distribution:")
    print(df["category"].value_counts().to_string())
    return df

def build_text_for_river(row):
    return f"{row['title']} {row['tags']} {row['description'][:200]}"

def train_online_model(df):
    print("[INFO] Training online learning model...")
    model = compose.Pipeline(
        feature_extraction.BagOfWords(lowercase=True),
        naive_bayes.MultinomialNB()
    )
    metric = metrics.Accuracy()
    trained = 0
    for _, row in df.iterrows():
        text = build_text_for_river(row)
        label = row["category"]
        pred = model.predict_one(text)
        if pred is not None:
            metric.update(label, pred)
        model.learn_one(text, label)
        trained += 1
        if trained % 50 == 0:
            print(f"[INFO] Trained on {trained} jobs | Accuracy: {metric.get():.2%}")
    print(f"[SUCCESS] Training complete!")
    print(f"[SUCCESS] Final accuracy: {metric.get():.2%}")
    print(f"[SUCCESS] Total jobs trained: {trained}")
    return model, metric

def save_model(model, metric):
    print("[INFO] Saving model...")
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    metrics_data = {
        "accuracy": metric.get(),
        "last_trained": datetime.now().isoformat(),
    }
    with open(METRICS_PATH, "wb") as f:
        pickle.dump(metrics_data, f)
    print(f"[SUCCESS] Model saved to {MODEL_PATH}")

def load_model():
    if not os.path.exists(MODEL_PATH):
        print("[WARNING] No model found, train first")
        return None
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    print("[SUCCESS] Model loaded")
    return model

def update_model(new_jobs):
    print("[INFO] Updating model with new jobs...")
    model = load_model()
    if model is None:
        return
    updated = 0
    for job in new_jobs:
        text = f"{job['title']} {job['tags']} {job['description'][:200]}"
        label = assign_category(job["title"])
        model.learn_one(text, label)
        updated += 1
    save_model(model, metrics.Accuracy())
    print(f"[SUCCESS] Model updated with {updated} new jobs")

def predict_category(title, tags, description):
    model = load_model()
    if model is None:
        return "unknown"
    text = f"{title} {tags} {description[:200]}"
    return model.predict_one(text)

if __name__ == "__main__":
    print(f"[INFO] Online Learning Started: {datetime.now()}")
    df = prepare_training_data()
    model, metric = train_online_model(df)
    save_model(model, metric)
    print(f"[INFO] Testing predictions:")
    test_titles = [
        ("Data Scientist", "python, ml, tensorflow", "We need a data scientist"),
        ("DevOps Engineer", "docker, kubernetes, aws", "Looking for devops engineer"),
        ("Software Engineer", "python, java, backend", "Backend software engineer role"),
        ("Data Analyst", "sql, tableau, excel", "Analyze business data"),
        ("ML Engineer", "pytorch, mlflow, python", "Build ML pipelines"),
    ]
    for title, tags, desc in test_titles:
        prediction = predict_category(title, tags, desc)
        print(f"  [{title}] -> {prediction}")