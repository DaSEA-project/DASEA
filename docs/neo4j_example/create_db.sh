#!/usr/bin/env bash

docker run \
    --name depgraphneo4j \
    -p7474:7474 -p7687:7687 \
    -d \
    -v $(pwd)/data:/var/lib/neo4j/import \
    --env NEO4J_AUTH=neo4j/password \
    neo4j:4.4.3

sleep 30
echo "Importing data..."
docker exec depgraphneo4j neo4j-admin import --force \
    --nodes=Package=/var/lib/neo4j/import/alire_packages_neo4j.csv \
    --nodes=Version=/var/lib/neo4j/import/alire_versions_neo4j.csv \
    --relationships=Dependency=/var/lib/neo4j/import/alire_dependencies_neo4j.csv \
    --relationships=VersionOf=/var/lib/neo4j/import/alire_instancerels_neo4j.csv \
    --skip-bad-relationships
sleep 20
docker container restart depgraphneo4j
