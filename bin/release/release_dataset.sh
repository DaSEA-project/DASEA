#!/usr/bin/env bash

datasetFileName=$(poetry run dasea release)
echo "$datasetFileName"

poetry run dasea push --sandbox --no-verify "data/out/$datasetFileName"
