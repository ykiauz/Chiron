import numpy as np
import torch
import json
import numpy as np
from sklearn import preprocessing
import copy

def select_random(data, k, current=None):
    indices = list(range(len(data)))
    ret = []
    while len(ret) < k:
        np.random.shuffle(indices)
        to_select = k - len(ret)
        selected = [data[i] for i in indices[:to_select] if data[i] not in ret and (current is None or data[i] not in current)]
        ret.extend(selected)
    return ret

metrics = {
    "disk-io": [31,78,34,61,2,1,13,5.1811,1.7141,0.5812,5.0E-4,8.25,3.69,0.0,135.68,0.0,0.0121],
    "factorial": [32,106,30,45,1,1,8,5.3942,1.8329,1.0039,5.0E-4,3.28,1.14,0.0,0.0,0.0,0.018727],
    "fibonacci": [23,109,20,34,1,1,6,5.4822,1.7445,1.0072,5.0E-4,3.24,0.85,0.0,0.0,0.0,0.01524],
    "pbkdf2": [22,124,34,56,1,2,11,9.3239,1.8212,1.0067,5.0E-4,3.02,1.25,0.0,0.0,0.0,0.013873],
    "pi": [35,117,48,78,2,2,16,8.2885,1.8281,1.0046,5.0E-4,4.21,0.96,0.0,0.0,0.0,0.01213],
    "network-io": [36,111,101,135,3,1,41,7.931,1.6034,0.4758,4.0E-4,88.45,9.16,0.0,0.0,35.17,0.056697],
    # "marketdata": [29,109,34,61,2,1,14,5.3015,1.6325,0.2137,3.0E-4,9.15,3.05,0.56,0.0,0.05,0.3939],
    "marketdata2": [9,124,29,58,1,1,14,9.2538,1.5546,0.0877,4.0E-4,14.69,2.54,0.0,0.0,0.01,0.1799],
    # "marketdata3": [8,115,22,48,1,1,9,5.7135,1.6901,0.0841,7.0E-4,17.81,2.66,0.0,0.0,0.01,0.238538],
    "lastpx": [25,118,47,89,3,1,21,8.1895,1.8048,0.6317,3.0E-4,6.9,2.23,0.0,0.0,0.0, 0.000129],
    "side": [17,104,28,55,1,1,14,8.3467,1.6887,0.6311,2.0E-4,5.73,1.86,0.0,0.0,0.0,0.000147],
    "trddate": [31,122,49,100,2,1,21,8.7313,1.7785,0.6148,3.0E-4,4.42,1.59,0.0,0.0,0.0,0.000155],
    "volume": [25,122,30,55,1,1,14,5.6861,1.7436,0.587,3.0E-4,5.25,1.9,0.0,0.0,0.0,0.000152],
    "margin-balance": [72,116,89,113,2,1,36,7.8059,1.6864,1.0097,3.0E-4,3.63,1.63,0.0,0.0,0.0,0.00026],
    "compose-review": [20,132,55,108,4,1,23,9.3629,1.5421,0.1962,3.0E-4,5.85,1.86,0.0,0.0,0.0,0.00004],
    "upload-user-id": [29,109,47,73,2,1,17,8.8046,1.6368,0.5868,5.0E-4,4.44,1.66,0.0,0.0,0.49,0.00202],
    "upload-movie-id": [26,115,49,78,3,1,15,8.7306,1.6682,0.8922,4.0E-4,5.88,1.7,0.0,0.0,1.2,0.00186],
    "mr-upload-text": [15,113,52,100,4,1,21,8.3739,1.6096,0.1752,3.0E-4,5.41,1.5,0.56,0.0,0.0,0.00005],
    "mr-upload-unique-id": [21,103,24,54,1,1,11,4.8724,1.6838,0.5453,3.0E-4,6.41,2.29,0.0,0.0,0.0,0.00013],
    "mr-compose-and-upload": [14,113,28,44,1,1,9,5.4294,1.5271,0.2708,3.0E-4,7.55,2.1,0.0,0.0,0.0,0.00017],
    "store-review": [15,107,26,47,1,1,12,7.748,1.6055,0.5997,5.0E-4,7.39,2.09,0.0,0.0,0.54,0.00193],
    "upload-user-review": [18,119,24,41,1,1,10,5.7795,1.601,0.6771,5.0E-4,11.85,4.61,0.0,0.0,6.45,0.00778],
    "upload-movie-review": [24,125,46,83,2,1,22,8.8125,1.6105,0.6765,5.0E-4,15.27,5.56,0.0,0.0,6.41,0.0076],
    "compose-post": [15,102,31,62,2,1,13,7.9816,1.6944,0.1561,3.0E-4,9.37,2.8,0.0,0.0,0.0,0.000047],
    "upload-media": [25,105,49,90,3,1,19,7.7346,1.6467,0.2176,3.0E-4,8.04,1.75,0.0,0.0,0.0,0.000074],
    "upload-creator": [23,15,5,8,0,0,1,0.9673,1.5529,0.8191,4.0E-4,51.49,2.55,0.0,0.0,0.78,0.001138],
    "upload-text": [14,126,23,38,1,1,8,6.2496,1.5416,0.3263,3.0E-4,10.7,2.35,0.0,0.0,0.0,0.000264],
    "upload-user-mentions": [26,107,29,49,1,1,9,5.5595,1.6557,0.7919,4.0E-4,31.48,3.02,0.0,0.0,1.15,0.002567],
    "upload-unique-id": [21,110,32,62,2,1,12,4.9119,1.6358,0.4771,3.0E-4,12.05,2.35,0.0,0.0,0.0,0.000144],
    "compose-and-upload": [16,104,37,80,2,1,17,7.4861,1.688,0.2791,3.0E-4,10.39,2.97,0.0,0.0,0.0,0.000260],
    "post-storage": [13,119,29,52,1,1,13,9.0666,1.5815,0.5867,5.0E-4,8.85,2.39,0.0,0.0,0.49,0.001861],
    "upload-user-timeline": [22,99,37,65,2,1,13,6.3737,1.5691,0.7017,4.0E-4,12.85,3.03,0.0,0.0,0.39,0.004129],
    "upload-home-timeline": [22,111,40,67,2,1,17,7.7589,1.6249,0.6771,5.0E-4,12.4,3.62,0.0,0.0,0.33,0.009212],
    # "process": [21,114,43,83,2,1,17,8.5221,1.7535,1.0031,4.0E-4,42.82,7.29,0.0,0.0,0.0, 0.003156]
    "process": [59,120,34,62,2,1,13,2.6709,1.7103,1.009,4.0E-4,56.62,7.78,0.0,0.0,0.0, 0.006684]
}


# for func_name in metrics:
#     for i in range(16):
#         metrics[func_name][i] = metrics[func_name][i] * metrics[func_name][-1]

min_max_scalar = preprocessing.MinMaxScaler()

# for i in range(16):
for i in range(17):
    keys = metrics.keys()
    values = [[v[i]] for v in metrics.values()]
    nor_values = min_max_scalar.fit_transform(values)

    for j, k in enumerate(keys):
        metrics[k][i] = nor_values[j][0]


# for k,v in metrics.items():
#     print(k, v)

num_dimensions = 56

stage_node_index_start = 25
partitions_node_index_start = 30

workflow_infos = {}
workflow_stages = {}


# suppose all workflow have 5 stages, each stage have 5 function
# fill workflow with fake node (metrics is set to [0] * 17)
def get_adjacency(workflow):
    stateName = workflow["StartAt"]
    state = workflow["States"][stateName]
    over = False
    current = 0
    stages = {}
    index_stages = []
    edges = []
    resources = {}
    indexs = {}
    tasks_per_stage = 5
    while not over:
        # edges.append((num_dimensions-1, stage_node_index_start+len(index_stages)))
        index_stages.append(stateName)
        current_num_stages = len(index_stages)
        if state["Type"] == "Task":
            stages[stateName] = stateName
            resources[stateName] = state["Resource"]
            # current_num_nodes = len(indexs)
            # indexs[stateName] = tasks_per_stage * (current_num_stages-1)
            indexs[stateName] = (current_num_stages-1, 0)
        elif state["Type"] == "Parallel":
            for branch_index, branch in enumerate(state["Branches"]):
                stages[branch["StartAt"]] = stateName
                resources[branch["StartAt"]] = branch["States"][branch["StartAt"]]["Resource"]
                # current_num_nodes = len(indexs)
                # indexs[branch["StartAt"]] = tasks_per_stage * (current_num_stages-1) + branch_index
                indexs[branch["StartAt"]] = (current_num_stages-1, branch_index)
        if "End" in state:
            over = True
        else:
            stateName = state["Next"]
            state = workflow["States"][stateName]

    adjacency = [0] * num_dimensions
    adjacency = [[0] * num_dimensions for _ in adjacency]

    # global node to stage node
    for i in range(5):
        adjacency[-1][stage_node_index_start+i] = 1

    # self loop
    # for i in range(num_dimensions):
    #     adjacency[i][i] = 1
        # global node
        # adjacency[num_dimensions-1][i] = 1

    return adjacency, indexs, resources, stages, index_stages

    # print(indexs)
    # print(edges)
    # print(resources)

def prepare_tensors(gs, targets=[0]):
    global workflow_infos

    features = []
    adjacencies = []
    stages = {}
    
    for g in gs:
        partitions = {}

        stage_map = {}
        if len(g.split("\t")) == 3:
            # [tg, workflow_name, stage_start_index] = g.split("\t")
            [tg, workflow_name, stage_map] = g.split("\t")
            stage_map = json.loads(stage_map)
            stage_start_index = 0
        else:
            [tg, workflow_name] = g.split("\t")
            stage_start_index = 0

        stage_start_index = int(stage_start_index)

        # workflow = json.loads(open("workflows/%s.json" % (workflow_name)).read())
        # adjacency, indexs, resources, stages, index_stages = get_adjacency(workflow)

        if workflow_name in workflow_infos:
            info = workflow_infos[workflow_name]
            indexs, resources, index_stages = info["indexs"], info["resources"], info["index_stages"]
            adjacency = copy.deepcopy(info["adjacency"])
            stages = workflow_stages[workflow_name]
        else:
            workflow = json.loads(open("workflows/%s.json" % (workflow_name)).read())
            adjacency, indexs, resources, stages, index_stages = get_adjacency(workflow)
            workflow_infos[workflow_name] = {
                "adjacency": copy.deepcopy(adjacency),
                "indexs": indexs,
                "resources": resources,
                "index_stages": index_stages
            }
            workflow_stages[workflow_name] = stages

        feature = [0] * num_dimensions
        
        # feature = [[0] * 18 for _ in feature]
        feature = [np.zeros(19, dtype=int) for _ in feature]

        policy = json.loads(tg)
        for v in policy.values():
            for i, groups in enumerate(v):
                for f in groups:
                    partitions[f] = i+1

        for f in resources:
            if f not in partitions:
                partitions[f] = 0

        # num_stages = len(set(stages.values()))

        tasks_per_stage = 5

        # fill task node
        task_node_start_index = stage_start_index * 5
        for v, k in indexs.items():
            temp_feature = metrics[resources[v]].copy()
            temp_feature.append(1)
            temp_feature.append(0)
            # fill fake node if no start from stage 0
            # if k[0] in stage_map:
            #     task_node_index = tasks_per_stage * stage_map[k[0]] + k[1]
            # else:
            #     task_node_index = tasks_per_stage * k[0] + k[1]

            task_node_index = tasks_per_stage * stage_map[str(k[0])] + k[1]

            feature[task_node_index] = np.array(temp_feature.copy())

        # fill fake stage node
        min_stage_index = min(stage_map.values())
        # if 0 in stage_map and stage_map[0] > 0:
        # for stage_index in range(stage_map[0]):
        for stage_index in range(min_stage_index):
            # stage node to partition node 0
            adjacency[stage_node_index_start+stage_index][partitions_node_index_start + stage_index * 5] = 1

            # partition node 0 to all fake stage task node
            stage_task_start_index = 5 * stage_index
            for i in range(stage_task_start_index, stage_task_start_index+5):
                adjacency[partitions_node_index_start + stage_index * 5][i] = 1

        # if len(stage_map) > 0:
        #     max_stage_index = max(len(index_stages), max(stage_map.values())+1)
        # else:
        #     max_stage_index = len(index_stages)
        max_stage_index = max(stage_map.values()) + 1
        # for stage_index in range(stage_start_index+len(index_stages), 5):
        for stage_index in range(max_stage_index, 5):
            # stage node to partition node 0
            adjacency[stage_node_index_start+stage_index][partitions_node_index_start + stage_index * 5] = 1

            # partition node 0 to all fake stage task node
            stage_task_start_index = 5 * stage_index
            for i in range(stage_task_start_index, stage_task_start_index+5):
                adjacency[partitions_node_index_start + stage_index * 5][i] = 1

        # fill real stage node
        for stage_index, stage_name in enumerate(index_stages):
            stage_fs = [f for f in partitions if stages[f] == stage_name]
            stage_fs_partitions = [partitions[f] for f in stage_fs]

            num_stages_partitions = max(stage_fs_partitions)+1

            # stage_fs_feature_list = []
            # for f in stage_fs:
            #     stage_fs_feature_list.append(metrics[resources[f]])

            # stage_fs_feature = np.sum(stage_fs_feature_list, axis=0)
            
            # stage_fs_feature = np.append(stage_fs_feature, [num_stages_partitions])

            # feature[stage_node_index_start+stage_index] = stage_fs_feature.copy()

            # fill partitions node
            # current_stage_index = stage_index
            # if current_stage_index in stage_map:
            #     current_stage_index = stage_map[current_stage_index]

            current_stage_index = stage_map[str(stage_index)]

            current_partitions_node_index_start = partitions_node_index_start + current_stage_index * 5

            # fill fake stage task node
            for i in range(len(stage_fs), 5):
                # fake partition 0 to stage task node
                adjacency[current_partitions_node_index_start][current_stage_index*5+i] = 1

            max_partition_index = 0
            max_partition_latency = 0
            for partition_index in range(num_stages_partitions):
                # stage node to partition node
                adjacency[stage_node_index_start+current_stage_index][current_partitions_node_index_start+partition_index] = 1

                current_partition_latency = 0

                # partition node to task node
                partition_fs = [f for f in stage_fs if partitions[f] == partition_index]
                for f in partition_fs:
                    # adjacency[current_partitions_node_index_start+partition_index][indexs[f]+task_node_start_index] = 1
                    adjacency[current_partitions_node_index_start+partition_index][tasks_per_stage * current_stage_index + indexs[f][1]] = 1
                    current_partition_latency += metrics[resources[f]][-1]

                # partition node self loop
                if partition_index > 0:
                    adjacency[current_partitions_node_index_start+partition_index][current_partitions_node_index_start+partition_index] = 1
                    partition_fs_feature = metrics["process"].copy()
                    partition_fs_feature.append(len(partition_fs))
                    partition_fs_feature.append(0)

                    current_partition_latency += metrics["process"][-1]
                else:
                    partition_fs_feature = [0] * 19
                    partition_fs_feature[-2] = len(partition_fs)

                if current_partition_latency > max_partition_latency:
                    max_partition_latency = current_partition_latency
                    max_partition_index = partition_index

                # partition_fs_feature_list = []
                # for f in partition_fs:
                #     partition_fs_feature_list.append(metrics[resources[f]])

                # partition_fs_feature = np.sum(partition_fs_feature_list, axis=0)
                # # partition_fs_feature.append(len(partition_fs))
                # partition_fs_feature = np.append(partition_fs_feature, [len(partition_fs)])

                feature[current_partitions_node_index_start+partition_index] = partition_fs_feature.copy()

            feature[current_partitions_node_index_start+max_partition_index][-1] = max_partition_latency
        # fill global node
        # stage_features_list = feature[stage_node_index_start:partitions_node_index_start]
        # global_node_feature = np.sum(stage_features_list, axis=0)
        # global_node_feature[-1] = 1
        
        # feature[-1] = global_node_feature.copy()

        adjacencies.append(adjacency)

        # print(feature)
        # print(adjacency)
        # exit(0)

        features.append(feature)

    adjacencies = torch.DoubleTensor(np.array(adjacencies))

    # print(np.array(features).shape)
    # exit(0)
    features = torch.DoubleTensor(np.array(features))
    # exit(0)

    labels = []
    for i in targets:
        labels.append([float(i)/1000])
        # labels.append([float(i)])
    labels = torch.DoubleTensor(labels)

    return adjacencies, features, labels


class Dataset():
    def __init__(self, target_workflow_name=""):
        self.target_workflow_name = target_workflow_name
        self.dataset = self._load_data()
        self.total_points = len(self.dataset)
        self.training_points = int(len(self.dataset) * 0.8)
        self.validation_points = int(len(self.dataset) * 0.2)

        self.train_set, self.valid_set, self.test_set = self._prepare_data()

    def _load_data(self):
        # with open("lats/lats_mr.csv", "r") as f:
        with open("lats/lats_no_%s_stru.csv" % self.target_workflow_name, "r") as f:
            lines = f.readlines()
            
        # print([d[1] for d in dataset])
        # exit(0)

        # return dataset

        # workflow_names = set()
        # for line in lines:
        #     workflow_names.add(line.split("\t")[1])

        # normalize(workflow_names)

        # workflows = {}        
        # for line in lines:
        #     workflow_name = line.split("\t")[1]
        #     if workflow_name not in workflows:
        #         workflows[workflow_name] = 1
        #     else:
        #         workflows[workflow_name] += 1

        # # print(workflows)
        # num_data_per_workflow = min(workflows.values())
        # print("Num data per workflow:", num_data_per_workflow)

        # dataset = []
        # for workflow_name in workflows:
        #     workflow_data = [line for line in lines if ("\t%s\t" % workflow_name) in line]
        #     if len(workflow_data) > num_data_per_workflow:
        #         dataset.extend(select_random(workflow_data, num_data_per_workflow))
        #     else:
        #         dataset.extend(workflow_data)

        dataset = lines
        dataset = [d.split("\t") for d in dataset]
        dataset = [["\t".join(d[:-1]), d[-1]] for d in dataset]

        np.random.shuffle(dataset)

        return dataset

    def _prepare_data(self):
        indices = list(range(self.total_points))
        
        np.random.shuffle(indices)
        training_indices = indices[:self.training_points]
        # validation_indices = indices[self.training_points:self.training_points+self.validation_points]
        validation_indices = indices[self.training_points:]
        # testing_indices = indices[self.training_points+self.validation_points:]
        testing_indices = indices[self.training_points:]

        training_data = [self.dataset[i] for i in training_indices]
        validation_data = [self.dataset[i] for i in validation_indices]
        testing_data = [self.dataset[i] for i in testing_indices]

        return training_data, validation_data, testing_data
