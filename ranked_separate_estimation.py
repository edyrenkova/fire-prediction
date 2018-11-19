import copy, random, math, os, json, time
from scipy import stats


def read_data(filename):
    """
    Reads data from the file.

    Parameters
    ----------
    filename : String
        The name of the file

    Returns
    -------
    list
        list of dictionaries read from the file
    """
    with open(filename) as f:
        data = json.load(f)
    return data


def choose_missing(data, percentage):
    """
    TESTING. Chooses the missing samples randomly according to percentage.

    Parameters
    ----------
    data : list
        The list of dictionaries containing samples to analyze
    percentage : float
        From 0.0 to 1.0. The percentage of samples to be missing

    Returns
    -------
    list of 2 lists
        list of two lists of dictionaries with data that is identified as missing and data without those values
    """
    number_missing = int(len(data) * percentage)
    result = [[], []]
    result[1] = copy.deepcopy(data)
    for i in range(number_missing):
        missing_id = random.randint(0, len(result[1]) - 1)
        #missing_id=i
        result[0].append(result[1][missing_id])
        result[1].remove(result[1][missing_id])
    return result

def get_missing(number, percentage):
    """
        TESTING. returns id numbers of missing values. Purpose - fix missing values for testing

        Parameters
        ----------
        percentage : float
            Number from 0 to 1 that is percent of data missing
        number: int
            total number of samples

        Returns
        -------
        list
            list of integers that are indices of missing samples
        """
    number_missing = int(number * percentage)
    missing_id = random.randint(0, number - 1)
    result=[]
    result.append(missing_id)
    for i in range(1,number_missing):
        missing_id = random.randint(0, number - 1)
        while missing_id in result:
            missing_id = random.randint(0, number - 1)
        result.append(missing_id)
    return result

def identify_missing():
    """
    identifies missing values in the list.

    Parameters
    ----------
    data : list
        The list of dictionaries containing samples to analyze

    Returns
    -------
    list
        list of dictionaries with data that is identified as missing
    """
    result = get_missing(45, 0.25)
    return result


def find_k_same_sensor(data):
    """
    finds the optimal number of the samples from the same sensor to be used in estimation. Data assumed to have only same sensor samples.

    Parameters
    ----------
    data : list
        The list of dictionaries containing samples to analyze

    Returns
    -------
    int
        the number of top-ranked samples to use in estimation
    """

    k = int(len(data)*0.7)
    return k

def find_k_same_time(data):
    """
    finds the optimal number of the samples from other sensors in the same time to be used in estimation. Data assumed to have only same time samples.

    Parameters
    ----------
    data : list
        The list of dictionaries containing samples to analyze

    Returns
    -------
    int
        the number of top-ranked samples to use in estimation
    """

    k = int(len(data)*0.7)
    return k

def find_distance(data1, data2):
    """
    finds spatial distance between two sensors from samples

    Parameters
    ----------
    data1,data2 : dictionary
        The dictionaries containing samples to find the the distance.

    Returns
    -------
    float
        number representing the distance between two sensors
    """
    long1 = data1['location']['longitude']
    lat1 = data1['location']['latitude']
    long2 = data2['location']['longitude']
    lat2 = data2['location']['latitude']
    # TODO: make it work for long and lat, for now assume x,y
    distance = math.sqrt(math.pow((float(long1) - float(long2)), 2) + math.pow((float(lat1) - float(lat2)), 2))
    return distance


def find_time_diff(data1, data2):
    """
    finds temporal distance between two sensors from samples

    Parameters
    ----------
    data1,data2 : dictionary
        The dictionaries containing samples to find the the temporal distance.

    Returns
    -------
    float
        number representing the temporal distance between two sensors
    """
    time1 = data1['timestamp']
    time2 = data2['timestamp']
    distance = abs(time1 - time2)
    return distance


def normalize(values):
    """
        normalizes dataset from 0.1 to 1.1

        Parameters
        ----------
        values : list
            The list of float numbers to normalize

        Returns
        -------
        list
            The list of float numbers normalized
        """
    maxim = max(values)
    minim = min(values)
    if minim==maxim and minim==0:
        for i in range(len(values)):
            values[i] = 0.1
    else:
        for i in range(len(values)):
            values[i] = 0.1 + ((values[i] - minim) * (1.1 - 0.1) / (maxim - minim))
    return values

def sort(data, missing_sample):
    """
    sorts data into three groups in regards to missing sample: time difference = 0, spatial distance = 0,
    the rest. Removes the samples from the rest that are from the same sensors as the first group.

        Parameters
        ----------
        data : list
            The list of dictionaries containing samples to analyze. missing values assumed to be removed

        missing_sample : dictionary
            A dictionary which is missing sample

        Returns
        -------
        list of 3 lists
            Three lists of dictionaries for each group. 0 - same sensor, 1 - same time, 2 - rest
        """
    result=[[],[],[]]
    data_copy=copy.deepcopy(data)
    data_copy=find_time_dist(data_copy,missing_sample)
    t_0=[]
    d_0=[]
    r=[]
    for item in data_copy:
        if item['time difference']==0:
            t_0.append(item)
        if item['distance']==0:
            d_0.append(item)
        else:
            r.append(item)
    r_1=copy.deepcopy(r)
   # for j in range(len(t_0)):
    #    for i in range(len(r)):
     #       if r[i]['device']['identifier']==t_0[j]['device']['identifier']:
      #          r_1.remove(r[i])
    result[0]=d_0
    result[1]=t_0
    result[2]=r_1
    return result


def weighted_average(data,missing_sample):
    """
        finds weighted average of k closest by distance to the missing one samples from data. assumed to have all the needed samples

        Parameters
        ----------
        data : list
            The list of dictionaries containing samples to analyze and weights towards the missing sample

        missing_sample : dictionary
            The dictionary containing missing samples

        Returns
        -------
        float
            the number that represents missing value
        """
    weight_sum=0
    data_copy=copy.deepcopy(data)
    result=0
    for i in range(len(data_copy)):
        distance=find_distance(data_copy[i],missing_sample)
        weight=1/distance
        data_copy[i]['weight']=weight
        weight_sum+=weight
    for i in range(len(data_copy)):
        result+=data_copy[i]['value']*(data_copy[i]['weight']/weight_sum)
    return result

def find_time_dist(data, missing_sample):
    data_copy=copy.deepcopy(data)
    for i in range(len(data_copy)):
        data_copy[i]['time difference']=find_time_diff(data_copy[i],missing_sample)
        data_copy[i]['distance'] = find_distance(data_copy[i], missing_sample)
    return data_copy

def linear_regression(data,missing_sample):
    """
        finds the prediction of the value of missing sample by linear regression based on the previous values of the same sensor. Data assumed to have only same sensor data.

        Parameters
        ----------
        data : list
            The list of dictionaries containing samples to analyze and weights towards the missing sample

        missing_sample : dictionary
            The dictionary containing missing samples

        Returns
        -------
        float
            the number that represents missing value estimation
    """
    times=[]
    values=[]
    for item in data:
        times.append(item['timestamp'])
        values.append(item['value'])
    slope, intercept, r_value, p_value, std_err = stats.linregress(times, values)
    estimation=intercept+slope*missing_sample['timestamp']
    return estimation

def estimate(data, missing_sample):
    """
    estimates data based on distance neighbors and time neighbors separately. Data is assumed to have distance and time difference fields

    Parameters
    ----------
    data : list
        The list of dictionaries containing samples to analyze and weights towards the missing sample

    missing_sample : dictionary
        The dictionary containing missing samples

    Returns
    -------
    dictionary
        the dictionary with estimated value
    """
    data=find_time_dist(data,missing_sample)
    sorted=sort(data,missing_sample)
    d_0=sorted[0]
    t_0=sorted[1]
    rest=sorted[2]
    kd=find_k_same_sensor(d_0)
    if kd>len(d_0):
        kd=len(d_0)
    kt=find_k_same_time(t_0)
    if kt>len(t_0):
        #kt=len(t_0)
        for i in range(kt-len(t_0)):
            list_lin = []
            item=find_min_dis(rest)
            predicted=copy.deepcopy(missing_sample)
            predicted['device']['identifier']=item['device']['identifier']
            predicted['location']['longitude'] = item['location']['longitude']
            predicted['location']['latitude'] = item['location']['latitude']
            list_lin.append(item)
            rest.remove(item)
            for i in range(len(rest)):
                if item['device']['identifier']==rest[i]['device']['identifier']:
                    list_lin.append(rest[i])
            list_lin=find_time_dist(list_lin,predicted)
            predicted['value']=linear_regression(list_lin,predicted)
            t_0.append(predicted)
            rest.remove(list_lin)
    neighbors=[]
    if kd>len(d_0):
        for i in range(kd):
            item=find_min_time_diff(data)
            neighbors.append(item)
            d_0.remove(item)
    else:
        neighbors=d_0
    if len(neighbors)<=1:
        kd=0
        estim_d=0
    else:
        estim_d=linear_regression(neighbors,missing_sample)
    neighbors=[]
    if kt>len(t_0):
        for i in range(kt):
            item=find_min_dis(data)
            neighbors.append(item)
            t_0.remove(item)
    else:
        neighbors=t_0
    estim_t=weighted_average(neighbors,missing_sample)
    weight_d_0=kd/(kd+kt)
    weight_t_0=kt/(kd+kt)
    estimation=estim_d*weight_d_0+estim_t*weight_t_0
    result=copy.deepcopy(missing_sample)
    result['value']=estimation
    return result

def find_min_dis(data):
    min_dis=data[0]
    for i in range(len(data)):
        if min_dis['distance']>data[i]['distance']:
            min_dis=data[i]
    return min_dis

def find_min_time_diff(data):
    min_dif=data[0]
    for i in range(len(data)):
        if min_dif['time difference']>data[i]['time difference']:
            min_dif=data[i]
    return min_dif


def find_error(real_samples, estimated_samples):
    """
    finds Root mean square error = sqrt(mean((estimation-real)^2)), mean is the average for all estimated values.

    Parameters
    ----------
    real_samples : list
        The list of dictionaries containing real samples which were assumed missing

    estimated_samples : list
        The list of dictionaries containing estimated samples

    Returns
    -------
    float
        the number which represents the RMSE for the testcase
    """
    errors_sum = 0
    for estim in estimated_samples:
        for real in real_samples:
            if estim['device']['identifier'] == real['device']['identifier'] and estim['timestamp'] == real['timestamp']:
                errors_sum += pow((estim['value'] - real['value']),2)
    result = math.sqrt(errors_sum / len(estimated_samples))
    return result


'''samples_num=[2,3,5,8,10]
for i2 in range(len(samples_num)):
    error_sum=0
    for i1 in range(50):
        real_samples = []
        estimated_samples = []
        missing_ids = get_missing(9*samples_num[i2], 0.25)
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
                estimated = estimate(data, missing)
                estimated_samples.append(estimated)
                data.append(estimated)
            #print(filename)
        error_sum+=find_error(real_samples, estimated_samples)
    print(error_sum/50)'''