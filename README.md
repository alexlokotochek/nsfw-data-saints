# nsfw-data-saints
```
Structure:
/prev -> BASEL + TF backend.
project with basel batch prediction. Works slower but better (data preparation is included)

/ -> KERAS
works few times faster but necessary to normalize images: (/255. - .5) * 2 and proper resize
```

# basel tensorflow serving docker-compose:

## [AWS EC2 container image: https://aws.amazon.com/marketplace/pp/B075DM6HV4]
```
$ curl -sSL https://raw.githubusercontent.com/bitnami/bitnami-docker-tensorflow-inception/master/docker-compose.yml > docker-compose.yml
$ docker-compose up -d
```


# docker-compose.yml:
```
version: '2'

services:
  tensorflow-serving:
    image: 'bitnami/tensorflow-serving:latest'
    ports:
      - '9000:9000'
    volumes:
      - 'tensorflow_serving_data:/bitnami'
      - '/tmp/model-data/:/bitnami/model-data'
  tensorflow-inception:
    image: 'bitnami/tensorflow-inception:latest'
    volumes:
      - 'tensorflow_inception_data:/bitnami'
      - '/tmp/model-data/:/bitnami/model-data'
    depends_on:
      - tensorflow-serving

volumes:
  tensorflow_serving_data:
    driver: local
  tensorflow_inception_data:
    driver: local
```


start docker container:
```
$ docker run -d -v /tmp/model-data:/bitnami/model-data -p 9000:9000 --name tensorflow-serving --net tensorflow-tier bitnami/tensorflow-serving:latest
```

start serving inception:
```
docker run -d --name tensorflow-inception \
  --net tensorflow-tier \
  --volume /path/to/tensorflow-inception-persistence:/bitnami \
  --volume /path/to/model_data:/bitnami/model-data \
  bitnami/tensorflow-inception:latest
```

# Prediction of 1000 classes from terminal basel inception client:
```
$ docker run --name tensorflow-inception -d bitnami/tensorflow-inception:latest
$ docker exec tensorflow-inception inception_client --server=SERVER_IP:9000 --image=/opt/bitnami/tensorflow-inception/tensorflow/tensorflow/contrib/ios_examples/benchmark/data/grace_hopper.jpg
```


# Python client:
```
auth.py; alco.py
```


# Structure:

```
/prev -> project with basel batch prediction. Works slower but better (data preparation is included)
/ -> using keras backend 
```
