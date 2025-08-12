#!/bin/bash
cd "$(dirname "$0")"
source mediahub-env/bin/activate
uvicorn main:app --host 0.0.0.0 --port 3000 --log-level info
