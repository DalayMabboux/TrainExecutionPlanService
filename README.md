# TrainExecutionPlanService

## Docker build locally
```docker build -t myimage .```

```docker run -d --name python-test -p 80:80 myimage```


### Azure
```docker login trainplanregistry.azurecr.io -u TrainPlanRegistry -p XXXXXX```

```docker build -t trainplanregistry.azurecr.io/trainplanservice:rc-1 .```

```docker push trainplanregistry.azurecr.io/trainplanservice:rc-1```

```bash
    curl -X 'POST' \
         'http://127.0.0.1:8000/evaluate-execution-plan' \
         -H 'accept: application/json' \
         -H 'Content-Type: application/json' \
         -d '{
     "train1_initial_position": 0,
     "train1_target_position": 0,
     "train2_initial_position": 0,
     "train2_target_position": 0,
     "switch_state": [
       0
     ]
   }'
```


Problem (ähnlich):
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/home/USER/venvs/torchgpu/lib/python3.10/site-packages/torch/__init__.py", line 239, in <module>
        from torch._C import *  # noqa: F403
    ImportError: /home/USER/venvs/torchgpu/lib/python3.10/site-packages/torch/lib/../../nvidia/cusparse/lib/libcusparse.so.12: undefined symbol: __nvJitLinkAddData_12_1, version libnvJitLink.so.12

Lösung:
    https://github.com/pytorch/pytorch/issues/111469
    Das habe ich gemacht:
        python -m pip uninstall torch
        python -m pip install --pre torch --index-url https://download.pytorch.org/whl/nightly/cu121

