# -*- coding: utf-8 -*-
'''
Created on 2016. jún. 29.

@author: padanyigulyasgergely
'''
import psycopg2
from tools.atool import Atool

class DbTool(object):

    # initialization
    def __init__(self, params):
        self.atool = Atool()
        self.con = None
        self.cur = None
        self.host = params.get("host")
        self.name = params.get("name")
        self.user = params.get("user")
        self.password = params.get("password")
        self.port = params.get("port")
    
    # connect to db
    def connect(self):
        try:
            self.con = None
            self.con = psycopg2.connect(host=self.host,
                                        database=self.name,
                                        user=self.user,
                                        password=self.password,
                                        port=self.port)
            self.cur = self.con.cursor()
        except Exception, e:
            self.atool.handle_exception(e)
            
    # closes the db connection together with the cursor
    def close(self):
        try:
            self.cur.close()
            self.con.close()
        except Exception, e:
            self.atool.handle_exception(e)
    
    # initializes the db (recreates the bbox table where the tiles are saved,
    # and the polygon table where the tiles should intesect, 
    # and it is populated with the wkt read from a file earlier
    def db_setup(self, crs, wkt):
        try:
            self.cur.execute("DROP TABLE IF EXISTS bbox")
            self.cur.execute("DROP TABLE IF EXISTS intersect_layer")
            self.cur.execute("CREATE TABLE bbox(id serial not null primary key, layer text, scale int, name text, geom geometry('Polygon', %s))" % crs)
            if wkt != None:
                self.cur.execute("CREATE TABLE intersect_layer(id serial not null primary key, geom geometry('MultiPolygon', %s))" % crs)
                self.cur.execute("INSERT INTO intersect_layer(geom) values(st_geomfromtext('%s', %s))" % (wkt, crs))
            self.con.commit()
        except Exception, e:
            self.atool.handle_exception(e)
    
    # save the tile in the db
    def i_bbox_store_in_db(self, layer, scale, minx, miny, maxx, maxy, geomfromtext, crs):
        try:
            self.cur.execute("INSERT INTO bbox(layer, scale, name, geom) values('%s', %s, '%s_%s_%s_%s', st_geomfromtext('%s', %s))" % (layer, scale, int(minx), int(miny), int(maxx), int(maxy), geomfromtext, crs))
            self.con.commit()
        except Exception, e:
            self.atool.handle_exception(e)