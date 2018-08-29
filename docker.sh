docker run \
    --publish=7474:7474 \
    --publish=7687:7687 \
    --volume=$PWD/data:/data \
    --volume=$PWD/logs:$PWD/logs \
    --name=$1 \
    neo4j