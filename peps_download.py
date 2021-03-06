#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-
import json
import time
import os, os.path, optparse,sys
from datetime import date

###########################################################################
class OptionParser (optparse.OptionParser):
 
    def check_required (self, opt):
      option = self.get_option(opt)
 
      # Assumes the option's 'default' is set to None!
      if getattr(self.values, option.dest) is None:
          self.error("%s option not supplied" % option)
 
###########################################################################

#==================
#parse command line
#==================
if len(sys.argv) == 1:
    prog = os.path.basename(sys.argv[0])
    print '      '+sys.argv[0]+' [options]'
    print "     Aide : ", prog, " --help"
    print "        ou : ", prog, " -h"
    print "example 1 : python %s -l 'Toulouse' -a peps.txt -d 2015-11-01 -f 2015-12-01"%sys.argv[0]
    print "example 2 : python %s --lon 1 --lat 44 -a peps.txt -d 2015-11-01 -f 2015-12-01"%sys.argv[0]
    print "example 3 : python %s --lonmin 1 --lonmax 2 --latmin 43 --latmax 44 -a peps.txt -d 2015-11-01 -f 2015-12-01"%sys.argv[0]
    sys.exit(-1)
else :
    usage = "usage: %prog [options] "
    parser = OptionParser(usage=usage)
  
    parser.add_option("-l","--location", dest="location", action="store", type="string", \
            help="town name (pick one which is not too frequent to avoid confusions)",default=None)		
    parser.add_option("-a","--auth", dest="auth", action="store", type="string", \
            help="Peps account and password file")
    parser.add_option("-w","--write_dir", dest="write_dir", action="store",type="string",  \
            help="Path where the products should be downloaded",default='.')
    parser.add_option("-c","--collection", dest="collection", action="store", type="choice",  \
            help="Collection",choices=['S1','S2','S3'],default='S2')
    parser.add_option("-i","--instrument", dest="instrument", action="store", type="choice",  \
                      help="Instrument (for Sentinel-3)",choices=['OLCI','SLSTR'],default='OLCI')
    parser.add_option("-m","--mode", dest="mode", action="store", type="choice",  \
                      help="Mode (for Sentinel-3 OLCI)",choices=['OL_1_EFR___','OL_1_ERR___','OL_1_RBT___'],default='OL_1_EFR___')
    parser.add_option("-n","--no_download", dest="no_download", action="store_true",  \
            help="Do not download products, just print curl command",default=False)
    parser.add_option("-d", "--start_date", dest="start_date", action="store", type="string", \
            help="start date, fmt('2015-12-22')",default=None)
    parser.add_option("--lat", dest="lat", action="store", type="float", \
            help="latitude in decimal degrees",default=None)
    parser.add_option("--lon", dest="lon", action="store", type="float", \
            help="longitude in decimal degrees",default=None)
    parser.add_option("--latmin", dest="latmin", action="store", type="float", \
            help="min latitude in decimal degrees",default=None)
    parser.add_option("--latmax", dest="latmax", action="store", type="float", \
            help="max latitude in decimal degrees",default=None)
    parser.add_option("--lonmin", dest="lonmin", action="store", type="float", \
            help="min longitude in decimal degrees",default=None)
    parser.add_option("--lonmax", dest="lonmax", action="store", type="float", \
            help="max longitude in decimal degrees",default=None)
    parser.add_option("-o","--orbit", dest="orbit", action="store", type="int", \
            help="Orbit Path number",default=None)
    parser.add_option("-f","--end_date", dest="end_date", action="store", type="string", \
            help="end date, fmt('2015-12-23')",default=None)

    (options, args) = parser.parse_args()

if options.location==None:    
    if options.lat==None or options.lon==None:
        if options.latmin==None or options.lonmin==None or options.latmax==None or options.lonmax==None:
            print "provide at least a point or rectangle"
            sys.exit(-1)
        else:
            geom='rectangle'
    else:
        if options.latmin==None and options.lonmin==None and options.latmax==None and options.lonmax==None:
            geom='point'
        else:
            print "please choose between point and rectangle, but not both"
            sys.exit(-1)
            
else :
    if options.latmin==None and options.lonmin==None and options.latmax==None and options.lonmax==None and options.lat==None or options.lon==None:
        geom='location'
    else :
          print "please choose location and coordinates, but not both"
          sys.exit(-1)
          
if geom=='point':
    query_geom='lat=%f\&lon=%f'%(options.lat,options.lon)
elif geom=='rectangle':
    query_geom='box={lonmin},{latmin},{lonmax},{latmax}'.format(latmin=options.latmin,latmax=options.latmax,lonmin=options.lonmin,lonmax=options.lonmax)
elif geom=='location':
    query_geom="q=%s"%options.location
    
if options.start_date!=None:    
    start_date=options.start_date
else :
    start_date=date(2015,01,01).isoformat()


if options.end_date!=None:
    end_date=options.end_date
else:
    end_date=date.today().isoformat()
#====================
# read authentification file
#====================
try:
    f=file(options.auth)
    (email,passwd)=f.readline().split(' ')
    if passwd.endswith('\n'):
        passwd=passwd[:-1]
    f.close()
except :
    print "error with password file"
    sys.exit(-2)



if os.path.exists('search.json'):
    os.remove('search.json')

if options.collection=='S3':
    if options.instrument=='OLCI':
        search_catalog='curl -k -o search.json https://peps.cnes.fr/resto/api/collections/%s/search.json?%s\&instrument=%s\&productType=%s\&startDate=%s\&completionDate=%s\&maxRecords=500'\
            %(options.collection,query_geom,options.instrument,options.mode,start_date,end_date)
    else:
        search_catalog='curl -k -o search.json https://peps.cnes.fr/resto/api/collections/%s/search.json?%s\&instrument=%s\&startDate=%s\&completionDate=%s\&maxRecords=500'\
            %(options.collection,query_geom,options.instrument,start_date,end_date) 
else :
    search_catalog='curl -k -o search.json https://peps.cnes.fr/resto/api/collections/%s/search.json?%s\&startDate=%s\&completionDate=%s\&maxRecords=500'%(options.collection,query_geom,start_date,end_date)

# search_catalog='curl -k -o search.json https://peps.cnes.fr/resto/api/collections/%s/search.json?%s\&startDate=%s\&completionDate=%s\&maxRecords=500'%(options.collection,query_geom,start_date,end_date)
    
print search_catalog
os.system(search_catalog)
time.sleep(5)

# Filter catalog result

with open('search.json') as data_file:    
    data = json.load(data_file)

if 'ErrorCode' in data :
    print data['ErrorMessage']
    sys.exit(-2)
    
#Sort data
download_list={}

for i in range(len(data["features"])):    
    prod=data["features"][i]["properties"]["productIdentifier"]
    feature_id=data["features"][i]["id"]

    if options.orbit!=None:
	if prod.find("_R%03d"%options.orbit)>0:
	    download_list[prod]=feature_id
            print prod,data["features"][i]["properties"]["startDate"]

    else:
        print prod,data["features"][i]["properties"]["startDate"]
	download_list[prod]=feature_id

#====================
# Download
#====================

if (not(options.no_download)):
    if len(download_list)==0:
        print "No product matches the criteria"
    else:
        for prod in download_list.keys():

            if options.write_dir==None :
                options.write_dir=os.getcwd()	
            file_exists= os.path.exists(("%s/%s.SAFE")%(options.write_dir,prod)) or  os.path.exists(("%s/%s.zip")%(options.write_dir,prod))
            tmpfile="%s/tmp.tmp"%options.write_dir
            print tmpfile
            get_product='curl -o %s -k -u %s:%s https://peps.cnes.fr/resto/collections/%s/%s/download/?issuerId=peps'%(tmpfile,email,passwd,options.collection,download_list[prod])
            print get_product
            if (not(options.no_download) and not(file_exists)):
                os.system(get_product)
                #check if binary product

                with open(tmpfile) as f_tmp:
                    try:
                        tmp_data=json.load(f_tmp)
                        print "Result is a text file"
                        print tmp_data
                        sys.exit(-1)
                    except ValueError:
                        pass

                os.rename("%s"%tmpfile,"%s/%s.zip"%(options.write_dir,prod))
                print "product saved as : %s/%s.zip"%(options.write_dir,prod)
            elif file_exists:
                print "%s already exists"%prod
            elif options.no_download:
                print "no download (-n) option was chosen"

else :
    print "no download (-n) option was chosen"
