project_root=$( cd "$(dirname "${BASH_SOURCE[0]}")/.." ; pwd -P )

if [[ ! -e ${project_root}/src/config/engine.json ]]; then
    echo "{}" > src/config/engine.json
    echo "wrote empty engine.json"
else
  echo "engine.json already exists"
fi
