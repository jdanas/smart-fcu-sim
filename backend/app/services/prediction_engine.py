import numpy as np
from sklearn.linear_model import LinearRegression
from typing import List, Tuple
from datetime import datetime


class PredictionEngine:
    """Simple linear regression-based temperature prediction."""

    def __init__(self, horizon_minutes: int = 15):
        self.horizon_minutes = horizon_minutes
        self.model = LinearRegression()
        self._min_samples = 5

    def predict(
        self, readings: List[float], interval_seconds: float = 5.0
    ) -> Tuple[float, float, str]:
        """
        Predict future temperature based on recent readings.

        Args:
            readings: List of recent temperature readings (oldest to newest)
            interval_seconds: Time interval between readings

        Returns:
            Tuple of (predicted_temp, confidence, trend)
        """
        if len(readings) < self._min_samples:
            # Not enough data - return last reading with low confidence
            current = readings[-1] if readings else 22.0
            return current, 0.5, "stable"

        # Prepare data for linear regression
        X = np.array(range(len(readings))).reshape(-1, 1)
        y = np.array(readings)

        # Fit model
        self.model.fit(X, y)

        # Calculate how many intervals into the future
        intervals_per_minute = 60 / interval_seconds
        future_intervals = int(self.horizon_minutes * intervals_per_minute)
        future_x = len(readings) + future_intervals

        # Predict
        predicted = self.model.predict([[future_x]])[0]

        # Clamp to reasonable range
        predicted = max(15.0, min(30.0, predicted))

        # Calculate confidence based on R² score and data consistency
        y_pred = self.model.predict(X)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)

        if ss_tot == 0:
            r2 = 1.0
        else:
            r2 = 1 - (ss_res / ss_tot)

        # Confidence is based on R² but also penalized for longer horizons
        confidence = max(0.3, min(0.95, r2 * 0.9))

        # Determine trend based on slope
        slope = self.model.coef_[0]
        if slope > 0.01:
            trend = "rising"
        elif slope < -0.01:
            trend = "falling"
        else:
            trend = "stable"

        return round(predicted, 2), round(confidence, 2), trend

    def get_prediction_series(
        self,
        readings: List[float],
        timestamps: List[datetime],
        interval_seconds: float = 5.0,
        points: int = 10,
    ) -> List[Tuple[datetime, float]]:
        """
        Generate a series of predictions for plotting.

        Returns list of (timestamp, predicted_temp) tuples.
        """
        if len(readings) < self._min_samples:
            return []

        X = np.array(range(len(readings))).reshape(-1, 1)
        y = np.array(readings)
        self.model.fit(X, y)

        results = []
        intervals_per_minute = 60 / interval_seconds

        for i in range(points):
            future_minutes = (i + 1) * (self.horizon_minutes / points)
            future_intervals = int(future_minutes * intervals_per_minute)
            future_x = len(readings) + future_intervals

            predicted = self.model.predict([[future_x]])[0]
            predicted = max(15.0, min(30.0, predicted))

            # Calculate future timestamp
            from datetime import timedelta

            future_time = timestamps[-1] + timedelta(minutes=future_minutes)

            results.append((future_time, round(predicted, 2)))

        return results


# Global instance
prediction_engine = PredictionEngine()
