import json, urllib.request, math, os, copy, ranked_separate_estimation


# loads json file and translates it into list of dictionaries
def read_data(filename):
    with open(filename) as f:
        data = json.load(f)
    return data


# finds K. Currently returns the number, could have algorithm in the future
def find_K(data):
    k=int(len(data)*0.7)
    if k==0:
        k=1
    return k

# finds the first item with the identifier given
def find_target(identifier, filename):
    data = load_json(filename)
    result = {}
    for item in data:
        if (item['device']['identifier'] == identifier):
            result.update(item)
    return result


# finds the items on the same floor. Argument has to be a dictionary. Use find_target
def find_same_floor(target, filename):
    data = load_json(filename)
    result = []
    for item in data:
        if (item['location']['floor'] == target['location']['floor']):
            result.append(item)
    return result


# finds spatiotemporal (euklidian distance with longitude, latitude and timestamp) distance between two sensors. Arguments are dictionaries
def find_distance(data1, data2):
    long1 = data1['location']['longitude']
    lat1 = data1['location']['latitude']
    time1 = data1['timestamp']
    long2 = data2['location']['longitude']
    lat2 = data2['location']['latitude']
    time2 = data2['timestamp']

    # TODO: make it work for long and lat, for now assume x,y
    distance = math.sqrt(
        math.pow((float(long1) - float(long2)), 2) + math.pow((float(lat1) - float(lat2)), 2) + math.pow(
            (float(time1) - float(time2)), 2))
    return distance


# returns dictionary that corresponds to the sensor with the minimum distance from target. Takes in dictionaries
def find_min_distance(data, target):
    min_distance = find_distance(target, data[0])
    min_data = data[0]
    for item in data:
        distance = find_distance(item, target)
        if (min_distance > distance):
            min_distance = distance
            min_data = item
    return min_data


# returns list of dictionaries of k nearest neighbors
def find_KNN(target, data):
    result = []
    data_copy=copy.deepcopy(data)
    k=find_K(data_copy)
    for i in range(k):
        min_dis = find_min_distance(data_copy, target)
        result.append(min_dis)
        data_copy.remove(min_dis)
        # print(data)
        # print(result)
    return result


# estimates value of target based on k nearest neighbors
def estimate(target, data):
    neighbors = find_KNN(target, data)
    #print(neighbors)
    k = find_K(data)
    values_sum = 0
    for i in range(len(neighbors)):
        values_sum += (float(neighbors[i]['value']))
    return values_sum / k


# returns percent error between estimate and real value
def find_error(estimated, real):
    if real == 0:
        return 100
    return abs(((estimated - real) / real) * 100)


missing_percent=[.05,.10,.15,.20,.40,.50]

for i2 in range(len(missing_percent)):
    error_sum = 0
    for i1 in range(50):
        real_samples = []
        estimated_samples = []
        #missing_ids = [22, 38, 39, 18, 43, 1, 7, 41, 23, 14, 4]
        missing_ids = ranked_separate_estimation.get_missing(9, missing_percent[i2])
        missing_list=[]
        for filename in os.listdir('C:/Users/dyren/Desktop/Datasets/9 sensors/15 sec/5 samples'):
            missing_list=[]
            data = read_data('C:/Users/dyren/Desktop/Datasets/9 sensors/15 sec/5 samples/' + filename)
            data_copy=copy.deepcopy(data)
            for i in range(len(missing_ids)):
                missing_list.append(data_copy[missing_ids[i]])
                data.remove(data_copy[missing_ids[i]])
            for missing in missing_list:
                real_samples.append(missing)
                #print(data)
                estimated=copy.deepcopy(missing)
                estimated_v = estimate(missing, data)
                estimated['value']=estimated_v
                estimated_samples.append(estimated)
                data.append(estimated)
        error=ranked_separate_estimation.find_error(real_samples, estimated_samples)
        #print(error)
        error_sum += error

    print(error_sum / 50)