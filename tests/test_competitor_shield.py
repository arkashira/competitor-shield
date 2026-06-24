from competitor_shield import CompetitorShield, CompetitorAlert

def test_generate_alert():
    shield = CompetitorShield()
    alert = shield.generate_alert("Product A", 0.8, ["Feature 1", "Feature 2"], "https://example.com")
    assert alert.product_name == "Product A"
    assert alert.similarity_score == 0.8
    assert alert.key_overlapping_features == ["Feature 1", "Feature 2"]
    assert alert.competitor_site_link == "https://example.com"

def test_send_alert():
    shield = CompetitorShield()
    alert = CompetitorAlert("Product A", 0.8, ["Feature 1", "Feature 2"], "https://example.com")
    shield.send_alert("user1", alert)
    assert len(shield.get_alerts("user1")) == 1

def test_dismiss_alert():
    shield = CompetitorShield()
    alert = CompetitorAlert("Product A", 0.8, ["Feature 1", "Feature 2"], "https://example.com")
    shield.send_alert("user1", alert)
    shield.dismiss_alert("user1", alert)
    assert len(shield.get_alerts("user1")) == 0

def test_snooze_alert():
    shield = CompetitorShield()
    alert = CompetitorAlert("Product A", 0.8, ["Feature 1", "Feature 2"], "https://example.com")
    shield.send_alert("user1", alert)
    shield.snooze_alert("user1", alert)
    assert len(shield.get_alerts("user1")) == 1

def test_get_alerts():
    shield = CompetitorShield()
    alert1 = CompetitorAlert("Product A", 0.8, ["Feature 1", "Feature 2"], "https://example.com")
    alert2 = CompetitorAlert("Product B", 0.9, ["Feature 3", "Feature 4"], "https://example.com")
    shield.send_alert("user1", alert1)
    shield.send_alert("user1", alert2)
    alerts = shield.get_alerts("user1")
    assert len(alerts) == 2

def test_is_alert_dismissed():
    shield = CompetitorShield()
    alert = CompetitorAlert("Product A", 0.8, ["Feature 1", "Feature 2"], "https://example.com")
    shield.send_alert("user1", alert)
    shield.dismiss_alert("user1", alert)
    assert shield.is_alert_dismissed("user1", "Product A") == True
