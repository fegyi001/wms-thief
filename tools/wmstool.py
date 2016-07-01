# -*- coding: utf-8 -*-
'''
Created on 2016. jún. 29.

@author: padanyigulyasgergely
'''
from StringIO import StringIO
import os
import urllib

from osgeo import gdal, osr, ogr
import requests

from PIL import Image
import numpy as np
from tools.atool import Atool


class WmsTool(object):

    # initialization
    def __init__(self, params):
        self.atool = Atool()
        self.dir = params.get("dir")
        self.scales = params.get("scales")
        self.url = params.get("url")
        self.crs = params.get("crs")
        self.width = params.get("width")
        self.height = params.get("height")
        self.layer = params.get("layer")
        self.image_format = params.get("image_format")
        self.wms_version = params.get("wms_version")
        self.styles = params.get("styles")
        self.startX = params.get("startx")
        self.startY = params.get("starty")
        self.endX = params.get("endx")
        self.endY = params.get("endy")
        self.wkt = params.get("wkt")
        self.db = params.get("db")
        self.clean_db = params.get("clean_db")
        
        # save the tiles in the main dir, under the dir of the layername...
        self.layerDir = self.__get_layerdir()
        # ...and beneath the dir of the according scale
        self.scaleDir = None
        
        # start bbox coordinates
        self.curMinX = None
        self.curMinY = None
        self.curMaxX = None
        self.curMaxY = None
        # start row y coordinate
        self.rowMinY = None
        
    # returns the main directory of the scales (from the layer name)
    def __get_layerdir(self):
        l = None
        # e.g. "workspace:layer" : ["workspace", "layer"]
        splitLayerByWorkspace = self.layer.split(":")
        if len(splitLayerByWorkspace) > 1:
            l = splitLayerByWorkspace[1]
        else:
            l = self.layer
        return r"%s\%s" % (self.dir, l)
        
    # the size of a tile in meters for a given scale
    def __get_size_in_meters(self, scale):
        return 716.8 * scale / 10000

    # puts together a WMS GetMap call url    
    def __get_getmap_url(self, scale, size):
        reqData = {"SERVICE": "WMS",
                   "VERSION": self.wms_version,
                   "REQUEST": "GetMap",
                   "FORMAT": "image/%s" % self.image_format,
                   "TRANSPARENT": "true",
                   "TILED": "true",
                   "STYLES": self.styles,
                   "LAYERS": self.layer,
                   "WIDTH": self.width,
                   "HEIGHT": self.height,
                   "CRS": "EPSG:%s" % self.crs,
                   "BBOX": "%d,%d,%d,%d" % (self.curMinX, self.curMinY, self.curMaxX, self.curMaxY)
                   }
        url = "%s?%s" % (self.url, urllib.urlencode(reqData)) 
        return url
    
    # jumps one row up
    def __step_one_up(self, size):
        self.rowMinY = self.rowMinY + size
        self.curMinX = self.startX
        self.curMinY = self.rowMinY
    
    # jumps one tile to the right
    def __step_one_right(self, size):
        self.curMinX = self.curMinX + size
    
    # creates georeferenced GeoTiff from the saved image
    def __transform_image(self, outputdir, filename, scale):
        try:
            src_filename = r"%s\%s.%s" % (outputdir, filename, self.image_format)
            dst_filename = r"%s\%s.tif" % (outputdir, filename)
            src_ds = gdal.Open(src_filename)
            driver = gdal.GetDriverByName("GTiff")
            dst_ds = driver.CreateCopy(dst_filename, src_ds, 0)
            # setting the transformation parameters
            gt = [self.curMinX,
                  (self.curMaxX - self.curMinX) / self.width,
                  0,
                  self.curMaxY,
                  0,
                  - (self.curMaxY - self.curMinY) / self.height]
            dst_ds.SetGeoTransform(gt)
            epsg = self.crs
            srs = osr.SpatialReference()
            srs.ImportFromEPSG(epsg)
            dest_wkt = srs.ExportToWkt()
            dst_ds.SetProjection(dest_wkt)
            dst_ds = None
            src_ds = None
            os.remove(src_filename)
        except Exception, e:
            self.atool.handle_exception(e)
            
    # save the WMS GetMap response image to the file system
    def __save_image_from_url(self, url, scale):
        try:
            filename = "%d_%d_%d_%d" % (int(self.curMinX), int(self.curMinY), int(self.curMaxX), int(self.curMaxY))
            fullfilename = r"%s\%s.%s" % (self.scaleDir, filename, self.image_format)
            print "        %s" % filename
            # the call itself
            r = requests.get(url)
            img = Image.open(StringIO(r.content))
            im = np.array(img)
            result = Image.fromarray(im)
            result.save(fullfilename)
            self.__transform_image(self.scaleDir, filename, scale)
        except Exception, e:
            self.atool.handle_exception(e)
    
    # retrieves and saves the image from the WMS server
    def __process_image(self, scale, size):
        minx = self.curMinX
        miny = self.curMinY
        maxx = self.curMaxX
        maxy = self.curMaxY
        # create WMS GetMap url
        url = self.__get_getmap_url(scale, size)
        # save image in the file system
        self.__save_image_from_url(url, scale)
        # store the tile and its metadata in the database
        if self.db != None:
            self.db.i_bbox_store_in_db(self.layer, scale,
                                       minx, miny, maxx, maxy,
                                       self.__get_geomfromtext(minx, miny, maxx, maxy),
                                       self.crs)
    
    # returns a wkt polygon from the bbox coordinates
    def __get_geomfromtext(self, minx, miny, maxx, maxy):
        return 'POLYGON((%s %s, %s %s, %s %s, %s %s, %s %s))' % (minx, miny,
                                                                     maxx, miny,
                                                                     maxx, maxy,
                                                                     minx, maxy,
                                                                     minx, miny)
    # performs a spatial intersection
    def __bbox_intersects_wkt(self, minx, miny, maxx, maxy):
        bbox = ogr.CreateGeometryFromWkt(self.__get_geomfromtext(minx, miny, maxx, maxy))
        return bbox.Intersects(self.wkt)
    
    # process the given row
    def __process_row(self, scale):
        size = self.__get_size_in_meters(scale)
        while self.curMinX < self.endX:
            self.curMaxX = self.curMinX + size
            self.curMaxY = self.curMinY + size
            # if a wkt is given use it as a mask, else process the tile anyway
            if self.wkt != None:
                # only make the url call if the given bbox intersects the mask polygon
                intersects = self.__bbox_intersects_wkt(self.curMinX, self.curMinY, self.curMaxX, self.curMaxY)
                if intersects:
                    self.__process_image(scale, size)
                    self.__step_one_right(size)
                else:
                    self.__step_one_right(size)
            else:
                self.__process_image(scale, size)
                self.__step_one_right(size)
        self.__step_one_up(size)
        self.atool.print_colors("    ... a row is completed at scale [%s]" % scale, self.atool.OKGREEN) 
    
    # process the given scale
    def __process_scale(self, scale):
        self.atool.print_colors("Processing scale [%s]..." % scale, self.atool.HEADER)
        # create a directory for the current scale
        self.scaleDir = r"%s\%s" % (self.layerDir, scale)
        if not os.path.isdir(self.scaleDir):
            os.makedirs(self.scaleDir)
        self.rowMinY = self.curMinY
        while self.rowMinY <= self.endY:
            self.__process_row(scale)
    
    # process all the scales
    def process_scales(self):
        if self.db != None:
            self.db.connect()
            if self.clean_db:
                self.db.db_setup(self.crs, self.wkt)
        # create an output folder with the layer name
        if not os.path.isdir(self.layerDir):
            os.makedirs(self.layerDir)
        for scale in self.scales:
            self.curMinX = self.startX
            self.curMinY = self.startY
            self.__process_scale(scale)
        self.atool.print_colors("All scales are processed!", self.atool.HEADER)
        if self.db != None:
            self.db.close()
