# Evaluation

This section provides the instructions of reproducing our evaluation, including [prediction error](https://github.com/ykiauz/Chiron/tree/main/Evaluation/prediction), [overall latency](https://github.com/ykiauz/Chiron/tree/main/Evaluation/latency) and [resource efficency](https://github.com/ykiauz/Chiron/tree/main/Evaluation/resource). We also provide the expected results in our environment.

## Wrap deployment
The following command will build the base images for all workflows and then deploy them:
```
cd wraps
./build.sh
./deploy.sh
```
