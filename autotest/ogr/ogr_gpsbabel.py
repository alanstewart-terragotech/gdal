#!/usr/bin/env python
###############################################################################
# $Id$
#
# Project:  GDAL/OGR Test Suite
# Purpose:  Test read functionality for OGR GPSBabel driver.
# Author:   Even Rouault <even dot rouault at mines dash paris dot org>
#
###############################################################################
# Copyright (c) 2010, Even Rouault <even dot rouault at mines-paris dot org>
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
###############################################################################



import gdaltest
import ogrtest
from osgeo import ogr
from osgeo import gdal
import pytest

###############################################################################
# Check that dependencies are met


def test_ogr_gpsbabel_init():

    # Test if the gpsbabel is accessible
    ogrtest.have_gpsbabel = False
    ogrtest.have_read_gpsbabel = False
    try:
        ret = gdaltest.runexternal('gpsbabel -V')
    except OSError:
        ret = ''
    if ret.find('GPSBabel') == -1:
        pytest.skip('Cannot access GPSBabel utility')

    ds = ogr.Open('data/test.gpx')

    if ds is None:
        print('GPX driver not configured for read support')
    else:
        ogrtest.have_read_gpsbabel = True

    ogrtest.have_gpsbabel = True

###############################################################################
# Test reading with explicit subdriver


def test_ogr_gpsbabel_1():

    if not ogrtest.have_read_gpsbabel:
        pytest.skip()

    ds = ogr.Open('GPSBabel:nmea:data/nmea.txt')
    assert ds is not None

    assert ds.GetLayerCount() == 2

###############################################################################
# Test reading with implicit subdriver


def test_ogr_gpsbabel_2():

    if not ogrtest.have_read_gpsbabel:
        pytest.skip()

    ds = ogr.Open('data/nmea.txt')
    assert ds is not None

    assert ds.GetLayerCount() == 2

###############################################################################
# Test writing


def test_ogr_gpsbabel_3():

    if not ogrtest.have_gpsbabel:
        pytest.skip()

    ds = ogr.GetDriverByName('GPSBabel').CreateDataSource('GPSBabel:nmea:tmp/nmea.txt')
    lyr = ds.CreateLayer('track_points', geom_type=ogr.wkbPoint)

    feat = ogr.Feature(lyr.GetLayerDefn())
    feat.SetField('track_fid', 0)
    feat.SetField('track_seg_id', 0)
    feat.SetField('track_name', 'TRACK_NAME')
    feat.SetField('name', 'PT_NAME')
    feat.SetField('hdop', 123)
    feat.SetField('vdop', 456)
    feat.SetField('pdop', 789)
    feat.SetField('sat', 6)
    feat.SetField('time', '2010/06/03 12:34:56')
    feat.SetField('fix', '3d')
    geom = ogr.CreateGeometryFromWkt('POINT(2.50 49.25)')
    feat.SetGeometry(geom)
    lyr.CreateFeature(feat)

    feat = None
    lyr = None
    ds = None

    f = open('tmp/nmea.txt', 'rt')
    res = f.read()
    f.close()

    gdal.Unlink('tmp/nmea.txt')

    assert (not (res.find('$GPRMC') == -1 or \
       res.find('$GPGGA') == -1 or \
       res.find('$GPGSA') == -1)), 'did not get expected result'




