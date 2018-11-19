import json,urllib.request, math, ranked_separate_estimation, copy, os

#loads json file and translates it into list of dictionaries
def read_data(filename):
    with open(filename) as f:
        data = json.load(f)
    return data

#finds K. Currently returns the number, could have algorithm in the future
def find_K():
    return 6

#finds the first item with the identifier given
def find_target(identifier,filename):
    data=load_json(filename)
    result={}
    for item in data:
        if(item['device']['identifier']==identifier):
            result.update(item)
    return result

#finds the items on the same floor. Argument has to be a dictionary. Use find_target
def find_same_floor(target,filename):
    data=load_json(filename)
    result=[]
    for item in data:
        if(item['location']['floor']==target['location']['floor']):
            result.append(item)
    return result

#finds spatial (euklidian distance with x,y) distance between two sensors. Arguments are dictionaries
def find_distance(data1,data2):
    long1=data1['location']['longitude']
    lat1=data1['location']['latitude']
    long2=data2['location']['longitude']
    lat2=data2['location']['latitude']
    #TODO: make it work for long and lat, for now assume x,y
    distance=math.sqrt(math.pow((float(long1)-float(long2)),2)+math.pow((float(lat1)-float(lat2)),2))
    return distance

#finds spatial (euklidian distance with x,y) distance between two sensors. Arguments are dictionaries
def find_time_diff(data1,data2):
    time1=data1['timestamp']
    time2=data2['timestamp']
    return abs(float(time1)-float(time2))
    

#returns dictionary that corresponds to the sensor with the minimum distance from target. Takes in dictionaries
def find_min_distance(data,target):
    min_distance=find_distance(target,data[0])
    min_data=data[0]
    for item in data:
        distance=find_distance(item,target)
        if((min_distance>distance)):
           #and item['device']['identifier']!=target['device']['identifier']):
            min_distance=distance
            min_data=item
    return min_data

#returns list of dictionaries of k nearest neigbors   
def find_KNN(target,filename):
    data=find_same_floor(target,filename)
    data.remove(target)
    result=[]
    for i in range(find_K()):
        min_dis=find_min_distance(data,target)
        result.append(min_dis)
        data.remove(min_dis)
    #print(result)
    return result

#finds the samples from the same sensor(distance = 0)
def find_time_neighbors(target,data_in):
    data=copy.deepcopy(data_in)
    result=[]
    for item in data:
        if(find_distance(item,target)==0):
            result.append(item)
    return result

#finds the samples from other sensors with the same timestamp (time diff=0)
def find_distance_neighbors(target,data_in):
    data=copy.deepcopy(data_in)
    result=[]
    for item in data:
        if(find_time_diff(item,target)==0 and item['location']['room']==target['location']['room']):
            result.append(item)
    return result

#estimates value of target based on nearest neighbors by time (of target sensor)
def estimate_by_time(target,data):
    neighbors=find_time_neighbors(target,data)

    #print('neighbors:')
    #print(neighbors)
    #print(neighbors)

    ###average from KNN
    #k=find_K()
    #values_sum=0
    #for i in range(len(neighbors)):
    #    values_sum+=(float(neighbors[i]['value']))
    #return values_sum/k

    ###linear interpolation with 2 values
    #v1=float(neighbors[0]['value'])
    #v2=float(neighbors[1]['value'])
    #t1=float(neighbors[0]['timestamp'])
    #t2=float(neighbors[1]['timestamp'])
    #t=float(target['timestamp'])
    #return (v1+(((v2-v1)/(t2-t1))*(t-t1)))

    ###weights based on 1/t

    #create list of time differences
    times=[]
    #stores the sum of 1/t
    weights_sum=0
    weights=[]
    for item in neighbors:
        time=item['timestamp']
        times.append(time)
        weights_sum+=float(time)
    for time in times:
        weight=time/weights_sum
        weights.append(weight)
    estimation=0
    for i in range(len(neighbors)):
        estimation+=neighbors[i]['value']*weights[i]
    result=copy.deepcopy(target)
    result['value'] = estimation
    return result

def linear_interpolation(target,data):
    neighbors=find_time_neighbors(target,data)
    v1=float(neighbors[0]['value'])
    v2=float(neighbors[1]['value'])
    t1=float(neighbors[0]['timestamp'])
    t2=float(neighbors[1]['timestamp'])
    t=float(target['timestamp'])
    return (v1+(((v2-v1)/(t2-t1))*(t-t1)))

#estimate by spatially close neighbors at the same time
def estimate_by_distance(target,filename):
    neighbors=find_distance_neighbors(target,filename)
    distances=[]
    weights_sum=0
    weights=[]
    for item in neighbors:
        distance=find_distance(item,target)
        distances.append(distance)
        weights_sum+=float(1/distance)
    for distance in distances:
        weight=float(((1/distance)/weights_sum))
        weights.append(weight)
    estimation=0
    for i in range(len(neighbors)):
        estimation+=neighbors[i]['value']*weights[i]
    result = copy.deepcopy(target)
    result['value'] = estimation
    return result

#returns percent error between estimate and real value.
def find_error(estimated,real):
    if(real==0):
        return 100
    return abs(((estimated-real)/real)*100)

samples_num=[2,3,5,8,10]
for i2 in range(len(samples_num)):
    error_sum = 0
    for i1 in range(50):
        real_samples = []
        estimated_samples = []
        missing_ids = ranked_separate_estimation.get_missing(9*samples_num[i2], 0.25)
        missing_list=[]
        for filename in os.listdir('C:/Users/dyren/Desktop/Datasets/9 sensors/15 sec/'+ str(samples_num[i2])+' samples'):
            missing_list=[]
            data = read_data('C:/Users/dyren/Desktop/Datasets/9 sensors/15 sec/'+ str(samples_num[i2])+' samples/' + filename)
            data_copy=copy.deepcopy(data)
            for i in range(len(missing_ids)):
                missing_list.append(data_copy[missing_ids[i]])
                data.remove(data_copy[missing_ids[i]])
            for missing in missing_list:
                real_samples.append(missing)
                #estimated_v = (estimate_by_time(missing,data)['value']+estimate_by_distance(missing, data)['value'])/2
                #estimated=copy.deepcopy(missing)
                #estimated['value']=estimated_v
                estimated = estimate_by_distance(missing, data)
                estimated_samples.append(estimated)
                data.append(estimated)
        error_sum +=ranked_separate_estimation.find_error(real_samples, estimated_samples)
    print(error_sum/50)