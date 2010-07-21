"""
 This module houses the GEOS ctypes prototype functions for the
 topological operations on geometries.
"""
__all__ = ['geos_boundary', 'geos_buffer', 'geos_centroid', 'geos_convexhull',
           'geos_difference', 'geos_envelope', 'geos_intersection', 
           'geos_linemerge', 'geos_pointonsurface', 'geos_preservesimplify',
           'geos_simplify', 'geos_symdifference', 'geos_union', 'geos_relate']

from ctypes import c_char_p, c_double, c_int
from django.contrib.gis.geos.libgeos import lgeos, GEOM_PTR, GEOS_PREPARE
from django.contrib.gis.geos.prototypes.errcheck import check_geom, check_string
from django.contrib.gis.geos.prototypes.geom import geos_char_p

def topology(func, *args):
    "For GEOS unary topology functions."
    argtypes = [GEOM_PTR]
    if args: argtypes += args
    func.argtypes = argtypes
    func.restype = GEOM_PTR
    func.errcheck = check_geom
    return func

### Topology Routines ###
geos_boundary = topology(lgeos.GEOSBoundary)
geos_buffer = topology(lgeos.GEOSBuffer, c_double, c_int)
geos_centroid = topology(lgeos.GEOSGetCentroid)
geos_convexhull = topology(lgeos.GEOSConvexHull)
geos_difference = topology(lgeos.GEOSDifference, GEOM_PTR)
geos_envelope = topology(lgeos.GEOSEnvelope)
geos_intersection = topology(lgeos.GEOSIntersection, GEOM_PTR)
geos_linemerge = topology(lgeos.GEOSLineMerge)
geos_pointonsurface = topology(lgeos.GEOSPointOnSurface)
geos_preservesimplify = topology(lgeos.GEOSTopologyPreserveSimplify, c_double)
geos_simplify = topology(lgeos.GEOSSimplify, c_double)
geos_symdifference = topology(lgeos.GEOSSymDifference, GEOM_PTR)
geos_union = topology(lgeos.GEOSUnion, GEOM_PTR)

# GEOSRelate returns a string, not a geometry.
geos_relate = lgeos.GEOSRelate
geos_relate.argtypes = [GEOM_PTR, GEOM_PTR]
geos_relate.restype = geos_char_p
geos_relate.errcheck = check_string

# Routines only in GEOS 3.1+
if GEOS_PREPARE:
    geos_cascaded_union = lgeos.GEOSUnionCascaded
    geos_cascaded_union.argtypes = [GEOM_PTR]
    geos_cascaded_union.restype = GEOM_PTR
    __all__.append('geos_cascaded_union')
