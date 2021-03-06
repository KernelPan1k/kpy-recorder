#!/usr/bin/env bash

mkdir dist/
cp -r ../../src ./src
cp ../../kpy_recorder.spec ./project.spec
cp ../../requirements.txt .
cp ../entrypoint-linux.sh .
docker build -t installer_linux_64 .
docker run -v "$(pwd)/dist:/usr/src/app/dist" installer_linux_64
mkdir -p ../../dist/linux_64 2>/dev/null
cp dist/linux/kpy_recorder ../../dist/linux_64