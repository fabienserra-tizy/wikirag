#!/usr/bin/env bash

# ******* Proxy and web server ******* #
export VHOST_TRAEFIK=wikirag.${DOCKER_USERNAME}.databird.io
export OPENAI_API_KEY="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"
export WEAVIATE_HOST="wikiragweaviate"
export WEAVIATE_HTTP_PORT=8080
export WEAVIATE_GRPC_PORT=50051
export WEAVIATE_DEFAULT_COLLECTION="NewCollection"
# If you want more:
#export VHOST_TRAEFIK_1=
#export VHOST_TRAEFIK_2=
# ...

# ******* Database definition #1 ******* #
#export MYSQL_DATABASE_USER_1=root
#export MYSQL_DATABASE_1=wikirag
#export OVERRIDE_DB_1=false
#export DB_BACKUP_PATTERN_1=wikirag.sql
#export DB_VOLUME_NAME_1=wikirag-dbdata
#export DB_ENTRYPOINT_1=db

# ******* Database definition #2 ******* #
#export MYSQL_DATABASE_USER_2=root
#export MYSQL_DATABASE_2=
#export OVERRIDE_DB_2=false
#export DB_BACKUP_PATTERN_2=
#export DB_VOLUME_NAME_2=
#export DB_ENTRYPOINT_2=

# ******* Database definition #n (20 max) ******* #
# ...