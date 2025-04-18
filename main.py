import os

from app.voc_monitor import VOCMonitor

voc_monitor = VOCMonitor()
voc_monitor.run()

for root, dirs, files in os.walk("E:/Bakalarka"):
    for file in files:
        if file == "database.db":
            print(os.path.join(root, file))
