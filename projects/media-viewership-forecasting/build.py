"""Build a reproducible rolling one-day forecast on synthetic daily viewership."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parent


def synthetic_data():
    rng = np.random.default_rng(2026)
    dates = pd.date_range("2025-01-01", periods=336)
    day = np.arange(len(dates))
    weekday_effect = np.array([-750, -550, -350, -100, 200, 1500, 1250])
    # Campaigns are scheduled in advance. Unplanned spikes are not features.
    planned_promo = np.isin(day % 23, [5, 6, 7]).astype(int)
    shock = np.zeros(len(day))
    shock[[54, 137, 232, 299, 316]] = [1700, 2200, 2600, 3200, 2900]
    noise = rng.normal(0, 390, len(day))
    for i in range(1, len(day)):
        noise[i] += 0.4 * noise[i - 1]
    views = np.rint(8500 + 9 * day + weekday_effect[dates.dayofweek] + 1850 * planned_promo + noise + shock).astype(int)
    return pd.DataFrame({"date": dates, "views": views, "planned_promo": planned_promo})


def prepare(data):
    d = data.copy()
    d["time_index"] = np.arange(len(d))
    for lag in (1, 7, 14):
        d[f"lag_{lag}"] = d["views"].shift(lag)
    d["mean_last_7"] = d["views"].shift(1).rolling(7).mean()
    for weekday in range(1, 7):
        d[f"weekday_{weekday}"] = (d["date"].dt.dayofweek == weekday).astype(int)
    return d.dropna().reset_index(drop=True)


def evaluate(data):
    d = prepare(data)
    features = [c for c in d if c not in {"date", "views"}]
    train = d[d.date < "2025-08-13"]
    val = d[(d.date >= "2025-08-13") & (d.date < "2025-09-24")]
    test = d[d.date >= "2025-09-24"].copy()
    assert train.date.max() < val.date.min() <= val.date.max() < test.date.min()
    scores = []
    for alpha in (0.1, 1, 10, 100):
        model = make_pipeline(StandardScaler(), Ridge(alpha=alpha))
        model.fit(train[features], train.views)
        scores.append((mean_absolute_error(val.views, model.predict(val[features])), alpha))
    alpha = min(scores)[1]
    dev = pd.concat([train, val])
    model = make_pipeline(StandardScaler(), Ridge(alpha=alpha))
    model.fit(dev[features], dev.views)
    test["yesterday"] = test.lag_1
    test["last_week"] = test.lag_7
    test["ridge"] = model.predict(test[features])
    metrics = pd.DataFrame([{
        "model": name,
        "mae": mean_absolute_error(test.views, test[name]),
        "rmse": np.sqrt(mean_squared_error(test.views, test[name])),
        "bias_pred_minus_actual": (test[name] - test.views).mean(),
    } for name in ("yesterday", "last_week", "ridge")])
    return test, metrics, scores, alpha, (len(train), len(val), len(test))


def draw(test, metrics):
    fig = plt.figure(figsize=(11, 6.5), facecolor="#edf4f7")
    fig.text(.05, .925, "Media Viewership Forecasting", fontsize=26, color="#142f43", weight="bold")
    fig.text(.05, .867, "Rolling one-day forecasts on later dates • Synthetic daily views", fontsize=13, color="#47657a")
    names = {"yesterday": "Yesterday", "last_week": "Same weekday last week", "ridge": "Ridge regression"}
    colors = {"yesterday": "#557084", "last_week": "#b96d48", "ridge": "#177e74"}
    for i, row in enumerate(metrics.itertuples(index=False)):
        fig.text(.05 + .32*i, .801, names[row.model], fontsize=12, color=colors[row.model], weight="bold")
        fig.text(.05 + .32*i, .753, f"{row.mae:,.0f} views MAE", fontsize=16, color="#142f43", weight="bold")
    ax = fig.add_axes([.09, .25, .86, .43], facecolor="white")
    ax.plot(test.date, test.views, color="#142f43", linewidth=1.8, label="Actual")
    ax.plot(test.date, test.last_week, color=colors["last_week"], linewidth=1.15, alpha=.75, label="Same weekday last week")
    ax.plot(test.date, test.ridge, color=colors["ridge"], linewidth=1.75, label="Ridge forecast")
    ax.set_ylabel("Daily views")
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.legend(loc="upper left", frameon=False, ncol=3)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#e3edf2")
    miss = test.loc[(test.views - test.ridge).idxmax()]
    fig.text(.05, .139, f"Largest underforecast: {miss.date:%b %d}, by {miss.views - miss.ridge:,.0f} views.",
             fontsize=13, color="#142f43", weight="bold")
    fig.text(.05, .088, "Use this as a planning baseline. Unplanned spikes remain a source of error.", fontsize=12, color="#47657a")
    fig.text(.05, .039, "Danish Syed / Synthetic data / No real audience or company data", fontsize=10, color="#47657a")
    fig.savefig(ROOT / "dashboard.png", dpi=125, facecolor=fig.get_facecolor())
    plt.close(fig)


def main():
    data = synthetic_data()
    test, metrics, scores, alpha, sizes = evaluate(data)
    data.to_csv(ROOT / "synthetic_views.csv", index=False, date_format="%Y-%m-%d")
    test[["date", "views", "planned_promo", "yesterday", "last_week", "ridge"]].to_csv(
        ROOT / "test_forecasts.csv", index=False, date_format="%Y-%m-%d", float_format="%.3f")
    metrics.to_csv(ROOT / "metrics.csv", index=False, float_format="%.3f")
    draw(test, metrics)
    print(f"Train/validation/test: {sizes}; selected alpha: {alpha}; validation MAE: {scores}")
    print(metrics.to_string(index=False))
    print(test.loc[(test.views - test.ridge).idxmax(), ["date", "views", "ridge"]].to_dict())


if __name__ == "__main__":
    main()
