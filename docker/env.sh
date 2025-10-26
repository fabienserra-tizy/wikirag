#!/usr/bin/env bash

# ******* Proxy and web server ******* #
export VHOST_TRAEFIK=wikirag.${DOCKER_USERNAME}.databird.io
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