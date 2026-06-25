from competitor_shield import AlertSystem, Threat

def test_add_threat():
    alert_system = AlertSystem()
    threat = Threat(1, "Test Threat", "High")
    alert_system.add_threat(threat)
    assert len(alert_system.get_threats()) == 1

def test_notify_users():
    alert_system = AlertSystem()
    threat1 = Threat(1, "Test Threat 1", "High")
    threat2 = Threat(2, "Test Threat 2", "Low")
    alert_system.add_threat(threat1)
    alert_system.add_threat(threat2)
    notification = alert_system.notify_users(alert_system.get_threats())
    assert "Competitive threats detected:" in notification
    assert "ID: 1, Name: Test Threat 1, Severity: High" in notification
    assert "ID: 2, Name: Test Threat 2, Severity: Low" in notification

def test_provide_insights():
    alert_system = AlertSystem()
    threat1 = Threat(1, "Test Threat 1", "High")
    threat2 = Threat(2, "Test Threat 2", "Low")
    alert_system.add_threat(threat1)
    alert_system.add_threat(threat2)
    insights = alert_system.provide_insights(alert_system.get_threats())
    assert "Actionable insights for competitive threats:" in insights
    assert "ID: 1, Name: Test Threat 1, Severity: High. Respond by monitoring and adjusting strategy." in insights
    assert "ID: 2, Name: Test Threat 2, Severity: Low. Respond by monitoring and adjusting strategy." in insights

def test_empty_threats():
    alert_system = AlertSystem()
    notification = alert_system.notify_users(alert_system.get_threats())
    assert notification == "Competitive threats detected:\n"
    insights = alert_system.provide_insights(alert_system.get_threats())
    assert insights == "Actionable insights for competitive threats:\n"
