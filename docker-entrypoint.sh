#!/bin/sh

python3 -m backup_jtekt
/bin/sh -c "sleep 300"
curl -s -X POST localhost:10001/quitquitquit
