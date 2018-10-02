
function docker_run {
    docker run \
        --publish=7474:7474 \
        --publish=7687:7687 \
        --volume=$PWD/data:/data \
        --volume=$PWD/logs:$PWD/logs \
        --env=NEO4J_dbms_allow__upgrade=true \
        --name=$1 \
    neo4j
}

function create_folder {
    rm -r data
    mkdir -p data/databases/graph.db
}

function create_d {
    create_folder
    cp -r drwho/* data/databases/graph.db
}

function create_c {
    create_folder
    cp -r cineasts/* data/databases/graph.db
}

function create_docker_folder {
    case "$1" in
    "-c")
        create_c
        echo "Creating cineasts dataset!"
        docker_run "$2"
        ;;
    "-d")
        create_d
        echo "Creating drwho dataset!"
        docker_run "$2"
        ;;
    *)
        echo "Creating empty dataset!"
        docker_run "$1"
        ;;
    esac
}

create_docker_folder "$1" "$2"
