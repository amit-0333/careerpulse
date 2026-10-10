import ast
import pandas as pd

src = open("model/online_learner.py", encoding="utf-8").read()
kw = None
for node in ast.parse(src).body:
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CATEGORY_KEYWORDS":
        kw = ast.literal_eval(node.value)

def cat(title):
    t = str(title).lower()
    for category, words in kw.items():
        if any(w in t for w in words):
            return category
    return "other_tech"

d = pd.read_csv("data/feature_store/jobs_features.csv")
print(d["title"].apply(cat).value_counts(normalize=True).round(3).to_string())