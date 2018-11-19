import json,xlrd,copy, time, estimator, random, xlwt

#reads the template json file and returns a dictionary
def read_template(filename):
    with open(filename) as f:
        data = json.load(f)
    return data

#returns the value of the cell of time/5 row a and sensor column
def read_data(time,sensor,filename):
    file=xlrd.open_workbook(filename)
    sheet = file.sheet_by_index(0)
    return sheet.cell_value(int((time/5)+3),int(sensor+1))

#returns x. sensor number starts from 0
def read_x(sensor,filename):
    file=xlrd.open_workbook(filename)
    sheet = file.sheet_by_index(0)
    return sheet.cell_value(1,int(sensor+1))

#returns y. sensor number starts from 0
def read_y(sensor,filename):
    file=xlrd.open_workbook(filename)
    sheet = file.sheet_by_index(0)
    return sheet.cell_value(2,int(sensor+1))

#returns updated template dictionary with data from arguments
def create_sample (time, sensor_num, x, y, value, template):
    result=copy.deepcopy(template)
    result['value']=value
    result['timestamp']=time
    result['device']['identifier']=sensor_num
    result['location']['longitude']=x
    result['location']['latitude']=y
    return result

#args have to be dictionaries. Saves json file
def create_json(*args):
    json_list=[]
    for arg in args:
        json_list.append(arg)
    with open('sensor_data.json','w') as f:
        json.dump(json_list,f)
    return json_list

# updates json file every update frequency with the data from three sensors
def create_stream(update_freq,template):

    file=xlwt.Workbook(encoding='ascii')
    sheet=file.add_sheet("1")
    sheet.write(0,0,'Error time')
    sheet.write(0,1,'Error distance')
    sheet.write(0,2,'Error lin inter')
    sheet.write(0,3,'Real')
    
    start=0
    end=start+int(update_freq/15)
    total_error=0
    x=0
    y=0
    counter=0
    for m in range(1,240,int(update_freq/15)):
        counter+=1
        samples=[]
        for i in range(int(start),int(end),1):
            for j in range(13):
                x=read_x(j,'sensor_temp_1room.xlsx')
                y=read_y(j,'sensor_temp_1room.xlsx')
                sample=create_sample(i*15,j,x,y,read_data(i,j,'sensor_temp_1room.xlsx'),template)
                samples.append(sample)
        file_out='15 sec, 3 samples/sensor_data'+str(m)+'.json'
        with open(file_out,'w') as f:
            json.dump(samples,f)
            #print(samples)
        start+=update_freq/15
        end+=update_freq/15

        #device=random.randint(0,12)
        device=7
        #error=estimator.find_error(estimator.find_target(device,'sensor_data.json'),file_out)
        print('device: '+str(device))
        real=estimator.find_target(device,file_out)['value']
        print("target")
        print(estimator.find_target(device,file_out))
        estimated_time=estimator.estimate_by_time(estimator.find_target(device,file_out),file_out)
        estimated_distance=estimator.estimate_by_distance(estimator.find_target(device,file_out),file_out)
        linear_interpolation=estimator.linear_interpolation(estimator.find_target(device,file_out),file_out)
        print("Real value:"+str(real))
        sheet.write(counter,3,real)
        print("Estimation by time neighbors: "+str(estimated_time))
        error=estimator.find_error(estimated_time,real)
        print("Percent error:"+str(error))
        sheet.write(counter,0,error)
        print("Estimation by distance neighbors: "+str(estimated_distance))
        error=estimator.find_error(estimated_distance,real)
        print("Percent error:"+str(error))
        sheet.write(counter,1,error)
        print("Estimation by linear interpolation: "+str(linear_interpolation))
        error=estimator.find_error(linear_interpolation,real)
        print("Percent error:"+str(error))
        sheet.write(counter,2,error)
        combined_est=(estimated_time+estimated_distance)/2
        print("Combined distance and time estimation: "+str(combined_est))
        error=estimator.find_error(combined_est,real)
        print("Percent error:"+str(error))
        sheet.write(counter,4,error)
    file.save('errors.xls')
    
template = read_template('sensor_template.json')
create_stream(60,template)

#device=random.randint(0,3)
#print('device: '+str(device))
#print("Real value:"+str(estimator.find_target(device,'sensors_data.json')['value']))
#print("Percent error:"+str(estimator.find_error(estimator.find_target(device,'sensors_data.json'))))
    
#sample1=create_sample(10,1,10,10,read_data(10,1,'sensor_data.xlsx'),template)
#sample2=create_sample(5,2,5,5,read_data(5,2,'sensor_data.xlsx'),template)
#print(create_json(sample1,sample2))
