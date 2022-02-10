IMAGE=g1g1/delinkcious-social-graph-reader:0.1

docker login -u $DOCKERHUB_USERNAME -p $DOCKERHUB_PASSWORD
docker build . -t $IMAGE
docker push $IMAGE