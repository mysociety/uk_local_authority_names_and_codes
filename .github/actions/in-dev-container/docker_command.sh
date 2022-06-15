docker-compose -f docker-compose.yml run --volume /home/runner:/home/runner/ app bash --noprofile --norc -eo pipefail $@
