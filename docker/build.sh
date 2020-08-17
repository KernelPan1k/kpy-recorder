#!/usr/bin/env bash

cd ./linux_64/ && ./build.sh && cd ..
cd ./linux_i386/ && ./build.sh && cd ..
cd ./win_64/ && ./build.sh && cd ..
cd ./win_32/ && ./build.sh && cd ..
