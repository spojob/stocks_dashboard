from asyncio import run, create_task, gather
from fill_timescaledb_timeseries import fill_timescaledb_timeseries
from fill_redis_timeseries import fill_redis_timeseries


async def main():
  fillers=[
    fill_redis_timeseries(), 
    fill_timescaledb_timeseries()
  ]
  tasks = [create_task(f) for f in fillers]
  await gather(*tasks)
  
if __name__ == '__main__':
    run(main())
