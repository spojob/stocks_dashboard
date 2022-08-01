# stocks_dashboard
Fake stocks realtime chart monitor

Architecture:
[Scrappers, ...] -> Queue --------------------------------------------> [ConsumerServices, ...]
                        |__> [StorageFillers, ...] -> [Storage, ...] -> [ConsumerServices, ...]

Main idea is to collect stocks data by Srappers and publish it to Queue
then queue sourced by Storage fillers and other data Consumer Services.
Also ConsumerServices can souce Strorages that filled by Storage fillers


To run stocks monitor
execute "docker-compose up" command in root folder "stocks_dashboard"

api service will be available on "http://localhost:8000"
dashboard service will be available on "http://localhost:8080"