# from dotenv import load_dotenv
# import os
# import requests

# load_dotenv()

# api_key = os.getenv("GROQ_API_KEY")

# response = requests.get(
#     "https://api.groq.com/openai/v1/models",
#     headers={
#         "Authorization": f"Bearer {api_key}"
#     }
# )

# print("Status:", response.status_code)

# data = response.json()

# if "data" in data:
#     print("Available models:")
#     for model in data["data"]:
#         print(model["id"])
# else:
#     print(data)

import pickle

with open("data/feature_store/model_metrics.pkl", "rb") as f:
    metrics = pickle.load(f)

print(f"Accuracy:     {metrics.get('accuracy', 0):.2%}")
print(f"Last trained: {metrics.get('last_trained', 'unknown')}")