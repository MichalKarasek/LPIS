#!/usr/bin/python
import sys
import argparse
import os
from io import StringIO
from io import *
from owslib.wfs import WebFeatureService
import xml.etree.ElementTree as ET
from owslib.fes import *
from owslib.etree import etree

def is_empty(response):
	"""Test whether area bounded by Bbox conatins elements
	"""	
	if isinstance(response, StringIO):
		root = ET.fromstring(response.read())
		if root[0][0].text == 'missing': 
			return False
		else:
			return True	
	else:
		return False
	
def process_service(layer_name, Bbox, tile_size, output, service, tiles):
	"""Split defined area in smaller parts
	"""
	def get_features(layer_name, Bbox, output, tile, tile_max):
		response = service.getfeature(layer_name, bbox = Bbox, srsname='urn:ogc:def:crs:EPSG::5514')
		data = is_empty(response)
		
		if data and tile_max != 1:
			store_response(output, response, tile, tile_max)
			return True
		elif data and tile_max == 1:
			response.seek(0)
			output.write(response.read())
		return False

	def validate_element(output, root, option):
		indent = True
		for featuremember in root.findall('{http://www.opengis.net/gml}featureMember'):
			resp = ET.tostring(featuremember, encoding = "unicode")
			resp = resp.replace('ns0','gml')
			resp = resp.replace('ns1','ms')
			resp = resp.replace(',','.')

			if indent:
				resp = '    '+resp
				indent = False
			output.write(resp)
		if option:	
			line = "</wfs:FeatureCollection>"+"\n\n"
			output.write(line)

	def store_response(output, response, tile, tile_max):
		
		response.seek(0)
		res = response.read()
		root = ET.fromstring(res)

		if tile == 1 and tile != tile_max:
			pattern = "</wfs:FeatureCollection>"+"\n\n"			
			res = res.replace(pattern,"")
			res = res.replace(',','.')
			output.write(res)
							
		elif tile != tile_max: validate_element(output, root, False)

		else : validate_element(output, root, True)
                
	area = abs(Bbox[0]-Bbox[2])*abs(Bbox[1]-Bbox[3])

	def process_all(layer_name, ycoordinates, xcoordinates, tile, tile_max, output):
		"""Process whole area
		"""
		y_west = ycoordinates[0]

		for i in range(1,len(ycoordinates)) :
			y_east = ycoordinates[i]
			x_north = xcoordinates[0]
			for j in range(1,len(xcoordinates)) :
				x_south = xcoordinates[j]
				Bbox = (y_west, x_north, y_east, x_south)
				data = get_features(layer_name, Bbox, output, tile, tile_max)
				if data:
					tile += 1
				else:
					tile_max -= 1
				x_north = x_south
			y_west = y_east

	def process_tiles(layer_name, ycoordinates, xcoordinates, tiles, output):
		"""Process only area specified by input tiles numbers
		"""
		t_incolumn = len(xcoordinates) - 1
		tile_max = len(tiles)
		tile = 1
		 		
		for t in tiles:
			y_pos = int(t/t_incolumn)
			x_pos = t - (y_pos*t_incolumn + 1)
			Bbox = [ycoordinates[y_pos],xcoordinates[x_pos],ycoordinates[y_pos+1],xcoordinates[x_pos+1]]
			data = get_features(layer_name, Bbox, output, tile, tile_max) 
			if data:
				tile += 1
			else:
				tile_max -= 1
	
	if area > tile_size*tile_size :
		"""Split in smaller parts
		"""
		ycoordinates = [i for i in range(Bbox[0], Bbox[2], tile_size)]
		xcoordinates = [i for i in range(Bbox[1], Bbox[3], tile_size)]
	
		tile = 1
		tile_max = len(xcoordinates)*len(ycoordinates)
		
		ycoordinates.append(Bbox[2])
		xcoordinates.append(Bbox[3])
		
		if tiles:
			process_tiles(layer_name, ycoordinates, xcoordinates, tiles, output)
		else:
			process_all(layer_name, ycoordinates, xcoordinates, tile, tile_max, output)

	else :
                get_features(layer_name, Bbox, output, 1, 1)

def show_layers(lpis):
	""" Show available layers from source
	"""
	for layer in lpis.contents:
		print(layer)

	sys.exit()

def validate_bbox(bbox):
	""" Check if bbox has right format
	"""
	if len(bbox) != 4:
		error = 'Uncorrect bbox size. Should be {0} is {1}!'.format(4,len(bbox))
		raise Exception(error)

if __name__ == "__main__":

	parser = argparse.ArgumentParser(description = 'Script for downloading wfs layers from LPIS', formatter_class = argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('layerName', type = str, help = 'Name of layer to download data from')
	parser.add_argument('tileSize', type = int, help = 'Length of tile size [m]')
	parser.add_argument('--Bbox', type = int, nargs = '+', default = (-904580,-1229235,-430007,-934219), help = 'Bounding area coordinates.')
	parser.add_argument('--layers', action = 'store_true',help = 'Type to get layers')
	parser.add_argument('--Tiles', type = int, nargs = '+', help = 'Enter numbers of tiles from Tile.py. Tile size must be set on same size.')

	args = parser.parse_args()

	bbox = args.Bbox
	validate_bbox(bbox)
	tiles = args.Tiles
	tile_size = args.tileSize
	layer_name = args.layerName
	lpis = WebFeatureService(url='http://eagri.cz/public/app/wms/plpis_wfs.fcgi', version = '1.1.0', timeout = 150)
	if args.layers: show_layers(lpis)

	file_name = '{}.gml'.format(layer_name.lower())
	with open(file_name,'w') as out:
		process_service(layer_name, bbox,tile_size, out, lpis, tiles)
