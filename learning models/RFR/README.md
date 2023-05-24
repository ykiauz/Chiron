# RFR model in Chiron's Evaluation
## Model input
We first profile 16 system-layer and microarchitecture-layer metrics for each function, including ContextSwitch, L1IMPKI, LIDMKPI, L2MPK2, TLBDMPKI, TLBIMPKI, BranchMPKI, L3MPKI, MLP, CpuUtil, MemUtil, MemBW, LLC, IPC, DiskIO and NetworkIO, which are recommended by the performance predictor Gsight [SC'21]. Then, we use the above metrics and solo-run latencies of functions in the same process as model input. 

## Model output
This model outputs the predicted latency of executing given functions in the same process. 
Then we use Equations 1-4 to calculate the end-to-end latency of given workflow.

## Environment

This model is run with Python 3.7, we list the necessary requirements in the following:

```
pip install numpy
pip install pandas
pip install Scikit-learn
```

## Training dataset
We collect all possible combinations of functions in each workflow, then generate training dataset for each workflow based on data other than it. For example, we train the model for FINRA-5 workflow using the data from social network, moive review, SLApp and SLApp. 
We have prepared the metrics of each function in tools/features directory. And the training data can be generated as following:
```
cd tools
python3 generate_features.py
python3 generate_train_data.py
```
The training dataset can be found in data directory.

## Training model
We train individual for seperate workflow. The following command will start training and output prediction error:
```
python3 RFR_model_training.py
```