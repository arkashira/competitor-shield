import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List

@dataclass
class CompetitorAlert:
    product_name: str
    similarity_score: float
    key_overlapping_features: List[str]
    competitor_site_link: str

class CompetitorShield:
    def __init__(self):
        self.alerts = {}
        self.dismissed_alerts = set()

    def generate_alert(self, product_name: str, similarity_score: float, key_overlapping_features: List[str], competitor_site_link: str) -> CompetitorAlert:
        alert = CompetitorAlert(product_name, similarity_score, key_overlapping_features, competitor_site_link)
        return alert

    def send_alert(self, user_id: str, alert: CompetitorAlert) -> None:
        if user_id not in self.alerts:
            self.alerts[user_id] = []
        self.alerts[user_id].append(alert)
        if len(self.alerts[user_id]) > 20:
            self.alerts[user_id].pop(0)

    def dismiss_alert(self, user_id: str, alert: CompetitorAlert) -> None:
        self.dismissed_alerts.add((user_id, alert.product_name))
        self.alerts[user_id] = [a for a in self.alerts[user_id] if a.product_name != alert.product_name]

    def snooze_alert(self, user_id: str, alert: CompetitorAlert) -> None:
        # Snooze logic can be implemented here
        pass

    def get_alerts(self, user_id: str) -> List[CompetitorAlert]:
        return self.alerts.get(user_id, [])

    def is_alert_dismissed(self, user_id: str, product_name: str) -> bool:
        return (user_id, product_name) in self.dismissed_alerts
