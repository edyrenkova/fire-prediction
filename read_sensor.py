import json, time, estimator, spidev,random

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000

def readadc(adcnum):
    if adcnum > 7 or adcnum < 0:
        return -1
    r = spi.xfer2([1, 8 + adcnum << 4, 0])
    adcout = ((r[1] & 3) << 8) + r[2]
    return adcout

def read_sensor_data(port):
    value = readadc(port)
    volts = (value * 3.3) / 1024
    return value
    

def load_json():
    with open('sensors.json') as f:
        data=json.load(f)
    return data

def update_data(data):
    for i in range(0,9,3):
        data[i]['value']=read_sensor_data(0)
        data[i]['timestamp']=time.time()
        data[i]['device']['identifier']=0
        data[i]['location']['longitude']=2
        data[i]['location']['latitude']=0
        data[i+1]['value']=read_sensor_data(2)
        data[i+1]['timestamp']=time.time()
        data[i+1]['device']['identifier']=1
        data[i+1]['location']['longitude']=4
        data[i+1]['location']['latitude']=0
        data[i+2]['value']=read_sensor_data(5)
        data[i+2]['timestamp']=time.time()
        data[i+2]['device']['identifier']=2
        data[i+2]['location']['longitude']=6
        data[i+2]['location']['latitude']=0
        data[i+3]['value']=read_sensor_data(6)
        data[i+3]['timestamp']=time.time()
        data[i+3]['device']['identifier']=3
        data[i+3]['location']['longitude']=8
        data[i+3]['location']['latitude']=0
        time.sleep(1)
    return data
        
def write_data(data):
    with open('sensors.json', 'w') as outfile:
        json.dump(data, outfile)

while(True):
    data=load_json()
    write_data(update_data(data))
    #print(data)
    #device=1
    device=random.randint(0,3)
    print('device: '+str(device))
    print("Real value:"+str(estimator.find_target(device,'sensors.json')['value']))
    print("Percent error:"+str(estimator.find_error(estimator.find_target(device,'sensors.json'))))
    
