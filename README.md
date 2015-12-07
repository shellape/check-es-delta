# check_es_delta.py

## Description
check_es_delta.py can be used to check the document growth of an elasticsearch instance.

Use cases:

* Check that the document growth does not fall under a specified threshold (default).
* Check that the document growth does not exceed a specified threshold.

check_es_delta.py uses the elasticsearch python module to communicate with elasticsearch's rest API. 


## Built in help
```
$> ./check_es_delta.py -h
usage: check_es_delta.py [-h] [-e es-url] [-i index-name] [-s status-file]
                         [-t min|max] -w threshold -c threshold

Get elasticsearch document count and calculate delta to previous script run
via status file.

optional arguments:
  -h, --help      show this help message and exit
  -e es-url       elasticsearch url (default: http://localhost:9200)
  -i index-name   index count to check (avoid param to check count of all
                  indices in sum) (default: )
  -s status-file  file to keep track (default: /tmp/es-delta.status)
  -t min|max      treat threshold as min or max (default: min)
  -w threshold    warning threshold (default: None)
  -c threshold    critical threshold (default: None)
```

## Hints
On first check invocation you will get a message like this:

"First run? No values from previous run in /tmp/es-delta.status available."

On next invocation there'll be data to compare.

## Examples
```
# Get the document delta for all indices:
$> check_es_delta.py -w 100 -c 0
OK: doc delta 3852 (i:,w:100,c:0,t:min) in 60.78s

# Get the document delta for a certain index:
$> check_es_delta.py -i logstash-apache-2015.12.07 -w 50 -c 0
OK: doc delta 4796 (i:logstash-syslog_2015.12.07,w:100,c:0,t:min) in 60.81s

```
