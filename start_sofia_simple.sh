#!/bin/bash
pkill -f "api.py" || true
cd /home/sofiaadmin/sofia/sofia
export SOFIA_USE_CLOUD=true
export GITHUB_TOKEN="${GITHUB_TOKEN:-}"
export GITHUB_MODEL=gpt-4o
if [ -z "$GITHUB_TOKEN" ]; then
	echo "ERRO: GITHUB_TOKEN nao definido no ambiente." >&2
	echo "Defina antes de executar: export GITHUB_TOKEN='seu_token_aqui'" >&2
	exit 1
fi
nohup /home/sofiaadmin/sofia/venv/bin/python api.py --host 0.0.0.0 --port 5000 > /tmp/sofia_output.log 2>&1 &
echo "Sofia iniciada"
sleep 8
echo "---LOG---"
cat /tmp/sofia_output.log
echo "---TESTE---"
curl http://localhost:5000/
