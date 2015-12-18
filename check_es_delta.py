#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
nagios compatible check.
Get the document count for all or a certain elasticsearch index.
Calculate the delta to the previous script invocation using a
status file. The value is compared to the specified thresholds.
'''
__author__ = 'vd@ghostshell.de'
__version__ = '0.1'

import os
import sys
import time
import argparse
import elasticsearch

# Global variables
RC = { 'OK':0, 'WARNING':1, 'CRITICAL':2, 'UNKNOWN':3 }

# Functions
def get_current_doc_count(es_url, index_name):
   '''Get document count from runniung elasticsearch instance.'''
   es = elasticsearch.Elasticsearch( [es_url] )
   count = es.cat.count(index_name).split(' ')[2]
   # Return count and epoch timestamp.
   return (int(count), time.time())

def get_previous_doc_count(status_file):
   '''Get document count from file.'''
   if os.path.exists(status_file):
      if os.path.isfile(status_file) and not os.path.islink(status_file):
         if os.access(status_file, os.R_OK):
            if os.path.getsize(status_file) > 0:
               with open(status_file, 'r') as fh:
                  (previous_doc_count, epoch_timestamp) = fh.readline().split()
         else:
            sys.stderr.write('{} is not readable.\n'.format(status_file))
            sys.exit(RC['UNKNOWN'])
      else:
         sys.stderr.write('{} is no regular file.\n'.format(status_file))
         sys.exit(RC['UNKNOWN'])

   try:
      return (int(previous_doc_count), float(epoch_timestamp))
   except UnboundLocalError:
      return ''

def write_current_doc_count(status_file, current_doc_count):
   '''Write count and timestamp to status file.'''
   with open(status_file, 'w') as fh:
      fh.write("{} {}".format(*current_doc_count))

def calc_deltas(current_doc_count, previous_doc_count):
   '''Calculate document and seconds delta.'''
   count1, seconds1 = current_doc_count
   count2, seconds2 = previous_doc_count
   return (count1 - count2, seconds1 - seconds2)
     
def check_threshold(doc_delta, 
                     seconds_delta,
                     threshold_type,
                     warning_threshold,
                     critical_threshold,
                     index_name):
   '''Check value with thresholds and exit with corresponding rc.'''

   warning_threshold = int(warning_threshold)
   critical_threshold = int(critical_threshold)

   if threshold_type == 'min':
      if doc_delta <= critical_threshold:
         state = 'CRITICAL'
      elif doc_delta <= warning_threshold:
         state = 'WARNING'
      else:
         state = 'OK'
   elif threshold_type == 'max':
      if doc_delta >= critical_threshold:
         state = 'CRTICAL'
      elif doc_delta >= warning_threshold:
         state = 'WARNING'
      else:
         state = 'OK'
   else:
      sys.stderr.write('Invalid argument "{}" for "-t".\n'.format(threshold_type))
      sys.exit(RC['UNKNOWN'])

   print('{}: doc delta {} (i:{},w:{},c:{},t:{}) in {:.2f}s'.format(state, 
                                                                     doc_delta,
                                                                     index_name,
                                                                     warning_threshold,
                                                                     critical_threshold,
                                                                     threshold_type,
                                                                     seconds_delta))
   sys.exit(RC[state])

def main():
   '''Main script body.'''
   # Parse argv.
   parser = argparse.ArgumentParser(
      formatter_class=argparse.ArgumentDefaultsHelpFormatter,
      description='Get elasticsearch document count and calculate delta \
                     to previous script run via status file.')
   parser.add_argument('-e',
      dest='es_url',
      metavar='es-url',
      default='http://localhost:9200',
      help='elasticsearch url')
   parser.add_argument('-i',
      dest='index_name',
      metavar='index-name',
      default='',
      help="index count to check (avoid param to check count of all indices in sum)")
   parser.add_argument('-s',
      dest='status_file',
      metavar='status-file',
      default='/tmp/es-delta.status',
      help='file to keep track')
   parser.add_argument('-t',
      dest='threshold_type',
      metavar='min|max',
      default='min',
      help='treat threshold as min or max')
   parser.add_argument('-w',
      dest='warning_threshold',
      metavar='threshold',
      required=True,
      help='warning threshold')
   parser.add_argument('-c',
      dest='critical_threshold',
      metavar='threshold',
      required=True,
      help='critical threshold')
   args = parser.parse_args()

   current_doc_count = get_current_doc_count(args.es_url, args.index_name)

   previous_doc_count = get_previous_doc_count(args.status_file)

   write_current_doc_count(args.status_file, current_doc_count)

   # On first run there won't be values to compare.
   if previous_doc_count == '':
      sys.stderr.write('First run? No values from previous run in {} available.\n'.format(args.status_file))
      sys.exit(RC['UNKNOWN'])
      
   (doc_delta, seconds_delta) = calc_deltas(current_doc_count, previous_doc_count)

   check_threshold(doc_delta, 
                     seconds_delta,                  
                     args.threshold_type,
                     args.warning_threshold,
                     args.critical_threshold,
                     args.index_name)

if __name__ == '__main__':
   main()
