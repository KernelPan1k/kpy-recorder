#!/usr/bin/env bash

cp -r ../../src .
cp ../../kpy_recorder.spec .
cp ../../requirements.txt .
cp ../entrypoint-windows.sh .
docker build -t installer_win_32 .
docker run --rm -v "$(pwd):/src/" installer_win_32
mkdir -p ../../dist/win_32 2>/dev/null
cp dist/windows/kpy_recorder.exe ../../dist/win_32