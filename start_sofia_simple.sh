#!/bin/bash
pkill -f "api.py" || true
cd /home/sofiaadmin/sofia/sofia
export SOFIA_USE_CLOUD=true
export GITHUB_TOKEN=ghp_REDACTED
export GITHUB_MODEL=gpt-4o
nohup /home/sofiaadmin/sofia/venv/bin/python api.py --host 0.0.0.0 --port 5000 > /tmp/sofia_output.log 2>&1 &
echo "Sofia iniciada"
sleep 8
echo "---LOG---"
cat /tmp/sofia_output.log
echo "---TESTE---"
curl http://localhost:5000/
