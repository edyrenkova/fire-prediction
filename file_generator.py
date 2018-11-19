import copy, xlrd, json
def read_template(filename):
    with open(filename) as f:
        data = json.load(f)
    return data

def generate_json(n, filename, template, total_samples, sensors_num,path): #n - samples per sensor in json file
    file = xlrd.open_workbook(filename)
    sheet = file.sheet_by_index(0)
    with open(template) as f:
        sample = json.load(f)
    for i in range(3,total_samples+3,n):
        samples = []
        for j in range(n):
            timestamp=sheet.cell_value(i+j+1,0)
            for k in range(sensors_num):
                sample_copy=copy.deepcopy(sample)
                sample_copy['location']['longitude']=sheet.cell_value(1,k+1)
                sample_copy['location']['latitude']=sheet.cell_value(2,k+1)
                sample_copy['value']=sheet.cell_value(i+j,k+1)
                sample_copy['timestamp']=timestamp
                sample_copy['device']['identifier']=k
                samples.append(sample_copy)
        file_out = path+'/sensor_data' + str(timestamp) + '.json'
        with open(file_out, 'w') as f:
            json.dump(samples, f)

generate_json(5,'C:/Users/dyren/Desktop/Datasets/13 sensors/15 sec.xlsx','sensor_template.json',240,13,'C:/Users/dyren/Desktop/Datasets/13 sensors/5 samples')