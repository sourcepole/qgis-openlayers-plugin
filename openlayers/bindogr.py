from osgeo import ogr, osr
import osgeo.gdalconst

def __getSpatialRefProj4(sProj4):
  sr = osr.SpatialReference()
  sr.ImportFromProj4(sProj4)
  return sr

def initOgr():
  ogr.RegisterAll()
def exportKml(wkt, proj4):
  geom = ogr.CreateGeometryFromWkt(wkt)
  sr = __getSpatialRefProj4(proj4)
  geom.AssignSpatialReference(sr)
  return geom.ExportToKML()
