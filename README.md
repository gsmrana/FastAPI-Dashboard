# Mediahub Dashboard
A FastAPI based dashboard app for media server.

## Setup and Run
1. Create a python virtual environment and activate it.
```
sudo apt install python3-venv python3-pip -y
cd /srv/Mediahub-Dashboard
python3 -m venv mediahub-env
source mediahub-env/bin/activate
pip install --upgrade pip
```

2. Install the required python packages.
```
pip install -r requirements.txt
```

3. Test standalone app from commnad line.
```
uvicorn main:app --host 0.0.0.0 --port 3000 --reload
```

4. Create a systemd daemon and run it.
```
sudo cp mediahub.service /etc/systemd/system/mediahub-daemon.service
sudo systemctl daemon-reload
sudo systemctl restart mediahub-daemon
```

5. Navigate to: **http://localhost:3000**
