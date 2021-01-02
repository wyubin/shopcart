#!/bin/bash
SCRIPT_PATH="$(readlink -f $0)"
SCRIPT_DIR="$(dirname $SCRIPT_PATH)"
SCRIPT_DIR2="$(dirname $SCRIPT_DIR)"
cd $SCRIPT_DIR2
## build image and container
commit=$(git rev-parse HEAD) docker-compose -f $SCRIPT_DIR/docker-compose.yml up -d --build
