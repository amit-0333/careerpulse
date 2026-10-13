"""Honest evaluation of the job-category model.

Run:  python -m mlops.evaluation
Compares the model with a majority-class baseline using repeated
stratified train/test splits, and prints per-class precision/recall.
"""
import json
import os
import numpy as np
import pandas as pd
from collections import Counter
from river import compose, feature_extraction, naive_bayes
from sklearn.metrics import classification_report, f1_score
from sklearn.model_selection import train_test_split
from model.online_learner import assign_category

FEATURES_CSV = "data/feature_store/jobs_features.csv"
EVAL_PATH = "data/feature_store/model_eval.json"
SEEDS = [0, 1, 2, 3, 4]


def text_current(row):  # what the deployed model sees today
    return f"{row['title']} {row['tags']} {str(row['description'])[:200]}"


def text_no_title(row):  # same job, but the title is hidden
    return f"{row['tags']} {str(row['description'])[:1000]}"


def new_model():
    return compose.Pipeline(
        feature_extraction.BagOfWords(lowercase=True),
        naive_bayes.MultinomialNB(),
    )


def evaluate(df, text_fn, label):
    texts = [text_fn(r) for _, r in df.iterrows()]
    y = df["category"].tolist()
    stratify = y if min(Counter(y).values()) >= 2 else None
    accs, base_accs, f1s, all_true, all_pred = [], [], [], [], []
    for seed in SEEDS:
        X_tr, X_te, y_tr, y_te = train_test_split(
            texts, y, test_size=0.2, random_state=seed, stratify=stratify
        )
        majority = Counter(y_tr).most_common(1)[0][0]
        model = new_model()
        for x, t in zip(X_tr, y_tr):
            model.learn_one(x, t)
        preds = [model.predict_one(x) or majority for x in X_te]
        accs.append(np.mean([p == t for p, t in zip(preds, y_te)]))
        base_accs.append(np.mean([majority == t for t in y_te]))
        f1s.append(f1_score(y_te, preds, average="macro", zero_division=0))
        all_true += y_te
        all_pred += preds
    result = {
        "input": label,
        "accuracy": float(np.mean(accs)),
        "accuracy_std": float(np.std(accs)),
        "baseline_accuracy": float(np.mean(base_accs)),
        "macro_f1": float(np.mean(f1s)),
        "n_jobs": len(df),
        "n_splits": len(SEEDS),
    }
    print("=" * 70)
    print(f"INPUT: {label}")
    print(f"  accuracy          : {result['accuracy']:.1%} (+/- {result['accuracy_std']:.1%})")
    print(f"  majority baseline : {result['baseline_accuracy']:.1%}")
    print(f"  macro F1          : {result['macro_f1']:.3f}  (1.0 = perfect, ignores class size)")
    print(classification_report(all_true, all_pred, zero_division=0))
    return result


def main():
    df = pd.read_csv(FEATURES_CSV)
    for col in ["title", "tags", "description"]:
        df[col] = df[col].fillna("")
    df["category"] = df["title"].apply(assign_category)
    print("Class share:", (df["category"].value_counts(normalize=True).round(3)).to_dict())
    results = [
        evaluate(df, text_current, "current model input (title + tags + description[:200])"),
        evaluate(df, text_no_title, "title hidden (tags + description[:1000])"),
    ]
    os.makedirs(os.path.dirname(EVAL_PATH), exist_ok=True)
    with open(EVAL_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved summary to {EVAL_PATH}")


if __name__ == "__main__":
    main()