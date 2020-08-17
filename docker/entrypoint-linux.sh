#!/bin/bash -i

set -e
. /root/.bashrc

if [[ "$@" == "" ]]; then
  if [ -f requirements.txt ]; then
    pip install --no-cache-dir -r requirements.txt
  fi

  pyinstaller --clean -y --dist ./dist/linux --workpath /tmp *.spec
  chown -R --reference=. ./dist/linux
else
  sh -c "$@"
fi
