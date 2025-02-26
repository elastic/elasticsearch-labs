# Running your own Elastic Stack with Docker

If you'd like to start Elastic locally, you can use the provided
[docker-compose-elastic.yml](docker-compose-elastic.yml) file. This starts
Elasticsearch, Kibana, and APM Server and only requires Docker installed.

Note: If you haven't checked out this repository, all you need is one file:
```bash
wget https://raw.githubusercontent.com/elastic/elasticsearch-labs/refs/heads/main/docker/docker-compose-elastic.yml
```

Before you begin, ensure you have free CPU and memory on your Docker host. If
you plan to use ELSER, assume a minimum of 8 cpus and 6GB memory for the
containers in this compose file.

First, start this Elastic Stack in the background:
```bash
docker compose -f docker-compose-elastic.yml up --force-recreate --wait -d
```

Then, you can view Kibana at http://localhost:5601/app/home#/

If asked for a username and password, use username: elastic and password: elastic.

Clean up when finished, like this:
```bash
docker compose -f docker-compose-elastic.yml down
```
