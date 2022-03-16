#!/usr/bin/env bash

datasetFileName=$(poetry run dasea release)
echo "$datasetFileName"

poetry run dasea push --no-verify "data/out/$datasetFileName"
