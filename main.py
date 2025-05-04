from app.voc_monitor import VOCMonitor

voc_monitor = VOCMonitor(
    "192.168.0.103",
    1883,
    8000
)
voc_monitor.run()
