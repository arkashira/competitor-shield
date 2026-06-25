import json
from dataclasses import dataclass
from typing import List

@dataclass
class Threat:
    id: int
    name: str
    severity: str

class AlertSystem:
    def __init__(self):
        self.threats = []

    def add_threat(self, threat: Threat):
        self.threats.append(threat)

    def get_threats(self) -> List[Threat]:
        return self.threats

    def notify_users(self, threats: List[Threat]) -> str:
        notification = "Competitive threats detected:\n"
        for threat in threats:
            notification += f"ID: {threat.id}, Name: {threat.name}, Severity: {threat.severity}\n"
        return notification

    def provide_insights(self, threats: List[Threat]) -> str:
        insights = "Actionable insights for competitive threats:\n"
        for threat in threats:
            insights += f"ID: {threat.id}, Name: {threat.name}, Severity: {threat.severity}. Respond by monitoring and adjusting strategy.\n"
        return insights
