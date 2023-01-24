from fastapi import FastAPI, Request
import os
from pydantic import BaseModel
from dateutil.parser import *
from dateutil.tz import *
from datetime import *
import redis

r = redis.Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), password=os.getenv("REDIS_PASS"))
awake = r.ping()

class TempReading(BaseModel):
    temp: float
    unit: str

app = FastAPI()

temp_readings = {}
temp_readings['sensors'] = {}
temp_readings['active_since'] = datetime.now()


@app.get("/")
async def root():
    return {"response": temp_readings}

@app.get("/readiness_check")
async def readiness_check():
    return {"response": 'I am ready.'}

@app.get("/liveness_check")
async def liveness_check():
    return {"response": 'I am alive.'}

@app.post("/temp")
async def post(temp_reading: TempReading, request: Request):
    f_temp = (temp_reading.temp * 1.8) + 24
    f_temp = round(f_temp, 2)
    unix_timestamp = int(datetime.now().strftime('%s'))
    temp_readings['sensors'][temp_reading.unit] = {
        "temp": f_temp,
        "ip": request.client[0],
        "current": datetime.now(),
    }
    temp_readings['count'] = len(temp_readings['sensors'])
    
    r.ts().add(temp_reading.unit, unix_timestamp, f_temp)
    return {"temp": temp_readings}

@app.post("/search")
async def search(request: Request):
    print('[POST] - SCAN')
    body = await request.body()
    return ['bedroom', 'solarium', 'livingroom', 'shower_room', 'kitchen', 'office', 'spare_bedroom', 'foyer']
    
# Translates JSON query to TS query
@app.post("/query")
async def query(request: Request):
    print("[POST] - QUERY")
    response = []
    body = await request.json()
    # set up iterator to query multiple TS and return in results_array
    targets = body['targets']
    for target_request in targets:
        target = target_request['target']
        
        print('target')
        print(target)

        from_time = body['range']['from']
        from_time = (parse(from_time) - timedelta(hours=8)).strftime('%s')


        to_time = body['range']['to']
        to_time = (parse(to_time) - timedelta(hours=8)).strftime('%s')

        aggregation_type = 'avg'
        
        interval = body['intervalMs']/1000
        results = r.ts().range(target, from_time, to_time, aggregation_type='avg', bucket_size_msec=5)

        results_list = []
        for index, tuple in enumerate(results):

            results_list.append([tuple[1], datetime.fromtimestamp(tuple[0]).strftime('%Y-%m-%d %H:%M:%S')])
            
        single_target_response = {
                            'target' : target,
                            'datapoints' : results_list
                    }
        response.append(single_target_response)
    
    return response