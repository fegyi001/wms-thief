# -*- coding: utf-8 -*-
'''
Created on 2016. jún. 29.

@author: padanyigulyasgergely
'''

from osgeo import ogr

from tools.atool import Atool
from tools.dbtool import DbTool
from tools.wmstool import WmsTool


atool = Atool()
dbParams = None
wmsParams = None


###########################
# USER DEFINED PARAMETERS #
###########################

# scales for wms requests
scales = [4000000, 2000000, 1000000]
# save directory in the file system
saveDir = r"E:\DATA\wms-thief_tiles"
# wms GetMap call parameters
url = "http://172.24.0.170:8080/geoserver/wms"
layer = "osmWsp:osm_hungary"
crs = 23700
width = 256
height = width
image_format = "png"
wms_version = "1.3.0"
styles = ""
# set the bounding box of the area to process
startX = 426402.66751693
startY = 43771.2799996209
endX = 937395.20651658
endY = 362942.143500254
# decide whether you wish to use a mask layer for the tiles or not
use_wkt = True
# decide whether you wish to store tile vectors and metadata in a PostGIS db
use_db = True
# decide whether you wish to clean the vector tiles in the db before processing
# it is recommended to set to True for the first run
# it is recommended to set to False if you have already processed a few scales and wish to continue 
# with another scales but want to keep the previous run's metadata
clean_db = True
# path to a wkt file for intersection checking
# it should be in the same crs as stored in the 'crs' variable (e.g. 23700)
# MANDATORY IF 'use_wkt' is set to True
wktFile = "data/wkt/intersect_layer_wkt.txt"
# database connection parameters
# MANDATORY IF 'use_db' is set to True
dbHost = 'localhost'
dbName = 'wmsthief'
dbUser = 'postgres'
dbPassword = 'passpostgres'
dbPort = '5435'


######################
# PREPARE FOR LAUNCH #
######################

if use_db:
    dbParams = {'host': dbHost,
                'name': dbName,
                'user': dbUser,
                'password': dbPassword,
                'port': dbPort}
wmsParams = {'dir': saveDir,
             'scales': scales,
             'url': url,
             'crs': crs,
             'width': width,
             'height': height,
             'layer': layer,
             'image_format': image_format,
             'wms_version': wms_version,
             'styles': styles,
             'startx': startX,
             'starty' : startY,
             'endx': endX,
             'endy': endY,
             'wkt': ogr.CreateGeometryFromWkt(atool.read_file_content(wktFile)) if use_wkt else None,
             'db': DbTool(dbParams) if use_db else None,
             'clean_db': clean_db}
wms = WmsTool(wmsParams)

###############
# THE PROGRAM #
###############

wms.process_scales()

