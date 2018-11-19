import copy, random, math, os, json, time, ranked_separate_estimation


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
        result[0].append(result[1][missing_id])
        result[1].remove(result[1][missing_id])
    return result


def identify_missing(data):
    """
    identifies missing values in the list and creates dictionaries for them with value=0

    Parameters
    ----------
    data : list
        The list of dictionaries containing samples to analyze

    Returns
    -------
    list
        list of dictionaries with data that is identified as missing
    """
    result = choose_missing(data, 0.7)
    return result


def find_k(data):
    """
    finds the optimal number of the samples to be used in estimation

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


def rank(data, missing_sample):
    """
    ranks the data in terms of similarity to missing sample

    Parameters
    ----------
    data : list
        The list of dictionaries containing samples to analyze. missing values assumed to be removed

    missing_sample : dictionary
        A dictionary which is missing sample

    Returns
    -------
    list
        The list of dictionaries with ranking in terms of similarity to the missing value.
    """
    result = copy.deepcopy(data)

    distances = []
    times = []
    for item in result:
        distances.append(find_distance(item, missing_sample))
    distances = normalize(distances)
    for item in result:
        times.append(find_time_diff(item, missing_sample))
    times = normalize(times)
    for i in range(len(result)):
        result[i]['distance']=distances[i]
        result[i]['time difference'] = times[i]
    for j in range(len(result)):
        result[j]['ranking'] = distances[j] * times[j]
    return result


def weigh(data, missing_sample):
    """
        weighs the data in terms of similarity to missing sample

        Parameters
        ----------
        data : list
            The list of dictionaries containing samples to analyze. missing values assumed to be removed

        missing_sample : dictionary
            A dictionary which is missing sample

        Returns
        -------
        list
            The list of dictionaries with weights in 'ranking' field in terms of similarity to the missing value.
        """
    result = copy.deepcopy(data)
    result_weights = []
    weights_sum = 0
    distances = []
    times = []
    for item in data:
        distances.append(item['distance'])
        times.append(item['time difference'])
    for j in range(len(result)):
        result_weights.append(1 / (distances[j] * times[j]))
        weights_sum += result_weights[j]
    for j in range(len(result_weights)):
        result[j]['ranking'] = result_weights[j] / weights_sum
    return result


def find_smallest_rank(data):
    min_rank_item = data[0]
    for item in data:
        if min_rank_item['ranking'] > item['ranking']:
            min_rank_item = item
    return min_rank_item


def estimate(data, missing_sample):
    """
    estimates data based on k top-ranked samples

    Parameters
    ----------
    data : list
        The list of dictionaries containing samples to analyze and weights towards the missing sample

    missing_sample : dictionary
        The dictionary containing missing samples

    k : int
        The number of used top-ranked samples

    Returns
    -------
    dictionary
        the dictionary with estimated value
    """
    result = copy.deepcopy(missing_sample)
    result_value = 0
    data_copy = copy.deepcopy(data)
    values = []
    ranking_sum = 0
    # print('used in estimation')
    for i in range(find_k(data_copy)):
        value = find_smallest_rank(data_copy)
        values.append(value)
        data_copy.remove(value)
    values = weigh(values, missing_sample)
    for i in range(len(values)):
        result_value += values[i]['value'] * values[i]['ranking']
    result['value'] = result_value
    return result


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
        the number from 0.0 to 1.0 which represents the RMSE for the testcase
    """
    errors_sum = 0
    for estim in estimated_samples:
        for real in real_samples:
            if estim['device']['identifier'] == real['device']['identifier'] and estim['timestamp'] == real['timestamp']:
                errors_sum += abs(estim['value'] - real['value'])
    result = errors_sum / len(estimated_samples)
    return result


'''samples_num=[2,3,5,8,10]
for i2 in range(len(samples_num)):
    error_sum = 0
    for i1 in range(50):
        real_samples = []
        estimated_samples = []
        missing_list = []
        missing_ids = ranked_separate_estimation.get_missing(9*samples_num[i2], 0.25)
        for filename in os.listdir('C:/Users/dyren/Desktop/Datasets/9 sensors/15 sec/'+ str(samples_num[i2])+' samples'):
            missing_list=[]
            data = read_data('C:/Users/dyren/Desktop/Datasets/9 sensors/15 sec/'+ str(samples_num[i2])+' samples/' + filename)
            data_copy=copy.deepcopy(data)
            for i in range(len(missing_ids)):
                missing_list.append(data_copy[missing_ids[i]])
                data.remove(data_copy[missing_ids[i]])
            for missing in missing_list:
                data = rank(data, missing)
                real_samples.append(missing)
                estimated = estimate(data, missing)
                estimated_samples.append(estimated)
        error_sum +=ranked_separate_estimation.find_error(real_samples, estimated_samples)
    print(error_sum/50)'''


