import argparse
import xml.etree.ElementTree as ET

def create_tiles(out, Bbox, size):
	"""Creates tiles of specified size on area bounded by bbox
	"""
	def write_header(out):
		xml = '<?xml'+" version='1.0' "+'encoding="UTF-8" '+'?>'
		ms = 'xmlns:ms="http://mapserver.gis.umn.edu/mapserver"'
		gml = 'xmlns:gml="http://www.opengis.net/gml"'
		wfs = 'xmlns:wfs="http://www.opengis.net/wfs"'

		out.write('<wfs:FeatureCollection'+'\n   '+ms+'\n   '+gml+'\n   '+wfs+'>')

	def create_gml(Bbox, out):
		"""Write geometry to gml
		"""
		geom = str(Bbox[0])+" "+str(Bbox[1])+" "+str(Bbox[0])+" "+str(Bbox[3])+" "+str(Bbox[2])+" "+str(Bbox[3])+" "+str(Bbox[2])+" "+str(Bbox[1])+" "+str(Bbox[0])+" "+str(Bbox[1])

		tile ='\n'+'  '+'<gml:featureMember>'+'\n'+'    '+'<ms:GEOMETRY>'+'\n'+'      '+'<gml:Polygon srsName="EPSG:5514">'+'\n'+"        "+'<gml:exterior>'+'\n'+"          "+'<gml:LinearRing>'+'\n'+"            "+'<gml:posList srsDimension="2">'+'\n'+geom+'</gml:posList>'+'\n'+"          "+'</gml:LinearRing>'+'\n'+'        '+'</gml:exterior>'+'\n'+'      '+'</gml:Polygon>'+'\n'+'    '+'</ms:GEOMETRY>'+'\n'+'  '+'</gml:featureMember>'

		out.write(tile)
		
	ycoordinates = [i for i in range(Bbox[0],Bbox[2],size)]
	xcoordinates = [i for i in range(Bbox[1],Bbox[3],size)]
		
	ycoordinates.append(Bbox[2])
	xcoordinates.append(Bbox[3])

	y_west = ycoordinates[0]
	write_header(out)

	for i in range(1,len(ycoordinates)) :
		y_east = ycoordinates[i]
		x_north = xcoordinates[0]
		for j in range(1,len(xcoordinates)) :
			x_south = xcoordinates[j]
			Bbox = (y_west, x_north, y_east, x_south)
			create_gml(Bbox, out)
			x_north = x_south
		y_west = y_east
	out.write('\n'+'</wfs:FeatureCollection>'+'\n')
	out.close()

if __name__ == "__main__":
	
	parser = argparse.ArgumentParser(description = 'Script for creating tiles', formatter_class = argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('--size', type = int, default = 4000, help = 'Length of tile side [m]')
	
	args = parser.parse_args()

	size = args.size
	bbox = (-904580,-1229235,-430007,-934219)
	file_name = 'tiles.gml'
	out = open(file_name, 'w')
	create_tiles(out, bbox, size)
