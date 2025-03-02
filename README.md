# TrainExecutionPlanService

## Docker build locally
```docker build -t myimage .```

```docker run -d --name python-test -p 80:80 myimage```

```docker login trainplanregistry.azurecr.io -u TrainPlanRegistry -p XXXXXX```


```docker build -t trainplanregistry.azurecr.io/trainplanservice:resttest-1 .```

```docker push trainplanregistry.azurecr.io/trainplanservice:resttest-1```
