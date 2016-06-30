# wms-thief
> batch WMS tile downloader and georeferencer

With ```wms-thief``` you can download WMS images from a server to your local machine. You can define multiple scales for a single run, the result images will be put in the folder named after the scale. The tile geometry and metadata are also saved in a PostGIS database in case you wish to visualize the tile vectors. 

After downloading, the images are georeferenced and converted into GeoTiff format, so you can easily add them to e.g. GeoServer as an image mosaic layer.

## Usage

1. To run ```wms-thief``` the usage of the OSGeo4W shell is recommended. You need to install the [requests](http://docs.python-requests.org/en/master/) package locally with pip: ```pip install requests``` ([this is how you install pip](https://trac.osgeo.org/osgeo4w/wiki/ExternalPythonPackages))
2. Modify the run.py file to match your needs
  * set the database connection
  * set the WMS parameters such as url, image format, layer, crs, starting-ending coordinates etc.
  * optionally add a [WKT (well-known-text)](https://en.wikipedia.org/wiki/Well-known_text) file containing a (multi)polygon for using as a mask layer
3. Run the program from the command line: ```python run.py```
5. Please do not download private or sensitive data

## Author
```wms-thief``` is created by [Gergely Padányi-Gulyás](http://www.gpadanyig.com)