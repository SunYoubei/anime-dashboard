# C:\Users\Iris\ml4biz\in-class\train_models.py
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import SGDRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "anime-dataset-2026.csv"

df = pd.read_csv(CSV_PATH)

for col in ["Score", "Members", "Scored By", "Favorites", "Episodes"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

feature_cols = ["Members", "Scored By", "Favorites", "Episodes"]
model_df = df.dropna(subset=["Score"] + feature_cols).copy()

X = model_df[feature_cols].values
y = model_df["Score"].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)


def evaluate(name, model, X_tr, X_te):
    model.fit(X_tr, y_train)
    pred = model.predict(X_te)
    return {
        "model": name,
        "RMSE": round(float(np.sqrt(mean_squared_error(y_test, pred))), 4),
        "MAE": round(float(mean_absolute_error(y_test, pred)), 4),
        "R2": round(float(r2_score(y_test, pred)), 4),
    }


results = [
    evaluate(
        "SGD Linear Regression",
        SGDRegressor(random_state=42, max_iter=1000),
        X_train_scaled,
        X_test_scaled,
    ),
    evaluate(
        "Random Forest",
        RandomForestRegressor(n_estimators=100, random_state=42),
        X_train,
        X_test,
    ),
]

print(pd.DataFrame(results).to_string(index=False))