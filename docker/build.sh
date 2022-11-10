
#!/bin/bash -eo pipefail

export CHECKM2_VERSION=`../bin/checkm2 --version`
export CHECKM2_DOCKER_VERSION=chklovski/checkm2:$CHECKM2_VERSION

cp ../checkm2.yml . && \
sed 's/CHECKM2_VERSION/'$CHECKM2_VERSION'/g' Dockerfile.in > Dockerfile && \
DOCKER_BUILDKIT=1 docker build -t $CHECKM2_DOCKER_VERSION . && \
docker run $CHECKM2_DOCKER_VERSION testrun && \
echo "Seems good - now you just need to 'docker push $CHECKM2_DOCKER_VERSION'"
