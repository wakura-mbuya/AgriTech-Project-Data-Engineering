"""Main module."""

import pdal
import json
import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon, Point, mapping
import numpy as np
from pyproj import Proj, transform
import folium
import laspy as lp

import warnings
import matplotlib.pyplot as plt
warnings.filterwarnings("ignore")

def add_one(number):
    """
    Adds 1 to the number. This function will be used for testing if the package is working fine

    params:
        number (int): a number to add 1 to
    """
    return number + 1

def read_json(json_path: str)->json:
    """
    This function loads a json file from a specified path into a json object
    
    params:
        json_path (str): the path to the json file
        
    returns:
        json object loaded from the json file
    """
    try:
        with open(json_path) as js:
            json_obj = json.load(js)
        return json_obj

    except FileNotFoundError:
        print('File not found.')
    
        
class AgriTech_Lidar():
    """
    This class can be used to connect to  USGS 3DEP dataset available to the public on AWS cloud and fetch the data. The class also includes functions to load the data 
    into a geo dataframe and methods to visualize the loaded data
    """
    
    def __init__(self, coordinates, region):
        """
        The constructor for the AgriTech_Lidar class
        
        params
            coordinates (list): coordinates of the section/area to be loaded
            region (str): The name of the region/state to load e.g 'IA_FullState'
        """
        self.json_path = "pdal.json"  #path to the json file for building the pdal pipeline
        self.url = "https://s3-us-west-2.amazonaws.com/usgs-lidar-public"   # url to the public lidar data on Amazon
        self.region = region  # the region we will be working with
        self.in_srs = 3857   # coordinate reference system used in the data on Amazon
        self.out_srs = 4326  # coordinate reference system we are going to use in the code.
        self.polygon = self.get_polygon(coordinates, 4326)
        
    def convert_EPSG(self, lon, lat, crs) -> list:
        """
        This function converts a coordinate from one coordinate system to another. The function can convert the coordinates from epsg 3857 coordinate system to epsg 
        4326 coordinate system and vice versa

        params:
            lon (double): the longitude value of the coordinate
            lat (double): the latitude value of the coordinate
            crs (int): the coordinate reference system of the coordinate to be converted

        returns: 
            A list of two values indicating the coordinate converted to the new system
        """
        P3857 = Proj(init='epsg:3857')
        P4326 = Proj(init='epsg:4326')
        if(crs == 4326):
            input1 = P4326
            input2 = P3857
        else:
            input1=p3857
            input2=p4326

        x, y = transform(input1,input2, lon, lat)
        return [x, y] 
    
    
    def EPSG_converter(self, coordinates_list: list) -> list:
        """
        This function converts of coordinates from the epsg 4326 coordinate reference system to 3857 reference system

        param:
            coordinates_list (list): list of coordinates to be converted

        returns:
            A list of the coordinates converted to the 3857 coordinates reference system
        """
        temp = []
        for item in coordinates_list:
            temp.append(convert_EPSG(item[0], item[1], 4326))

        return temp
    
    
    def get_polygon(self, coor, epsg):
        """
        This function generates a GPS coordinates polygon from the list of coordinates

        params:
            coor (list): A list of coordinates to be included in the polygon
            epsg (int):  The coordinate reference sysem of the coordinates in the list

        returns:
            A GPS coordinates Polygon
        """
        polygon_g = Polygon(coor)
        crs = {'init': 'epsg:'+str(epsg)}
        polygon = gpd.GeoDataFrame(index=[0], crs=crs, geometry=[polygon_g])       
        return polygon
    
    
    def get_geoDf(self, pipe, epsg):
        """
        Generates a Geo Dataframe after executing the pdal pipeline

        params:
            pipe (Pipeline): a pdal pipeline
            epsg (int): coordinate reference system

        returns:
            A Geo Dataframe
        """
        try:
            cloud_points = []
            elevations =[]
            geometry_points=[]
            for row in pipe.arrays[0]:
                lst = row.tolist()[-3:]
                cloud_points.append(lst)
                elevations.append(lst[2])
                point = Point(lst[0], lst[1])
                geometry_points.append(point)
            geodf = gpd.GeoDataFrame(columns=["elevation", "geometry"])
            geodf['elevation'] = elevations
            geodf['geometry'] = geometry_points
            geodf = geodf.set_geometry("geometry")
            geodf.set_crs(epsg = epsg, inplace=True)
            return geodf
        except RuntimeError as e:
            self.logger.exception('Could not generate the Geo Dataframe')
            print(e) 
            
    def build_pipeline(self, json_path, url, region, in_epsg, out_epsg):
        """
        This function builds the json file that is used to build the pdal pipeline

        params:
            json_path (str): Path to the initial json file
            url (str): The url to the public lidar data on AWS
            in_epsg (int): coordinate reference system used in the data on AWS
            out_epsg (int): coordinate reference system to be used on the data returned

        returns:
            json object to be used to build and execute the pdal pipeline for fetching the data
        """
        temp = read_json(json_path)
        temp['pipeline'][0]['polygon'] = str(polygon.iloc[:,0][0])
        temp['pipeline'][0]['filename'] = f"{url}/{region}/ept.json"
        temp['pipeline'][2]['in_srs'] = f"EPSG:{in_epsg}"
        temp['pipeline'][2]['out_srs'] = f"EPSG:{out_epsg}"
        print(temp)   #for testing
        return temp
    
    def show_on_map(self, polygon, zoom):
        """
        Represents polygon on a map, zoomed to a specified percentage

        params:
            polygon (Polygon): The GPS coordinates polygon to be represented on the map
            zoom (int): The percetage to zoom to
        """
        poly = mapping((polygon.iloc[:,0][0]))  #region selection
        tmp = poly['coordinates'][0][0]
        anchor = [tmp[1], tmp[0]]
        m = folium.Map(anchor,zoom_start=zoom, tiles='cartodbpositron')
        folium.GeoJson(polygon).add_to(m)
        folium.LatLngPopup().add_to(m)
        return m
    
    def plot_heatmap(self, geo_df, title) -> None:
        """ 
        Plots a 2D heat map for the point cloud data using matplotlib
        This function also saves the plot as a picture
        Params:
            geo_df (geoDataframe): A geo DataFrame of the points
            title (str): A title for the plot
        """

        fig, ax = plt.subplots(1, 1, figsize=(12, 10))
        geo_df.plot(column='elevation', ax=ax, legend=True, cmap="terrain")
        plt.title(title)
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.savefig('Terrain_heatmap.png', dpi=120)
        plt.show()
        
        
    def render_3d(points, s: float = 0.01) -> None:
        """ 
        Plots a 3D terrain scatter plot for the cloud data points of geopandas data frame using matplotlib
        This function also saves the 3d plot as a picture

        params:
            points: points to be plotted
        """

        fig, ax = plt.subplots(1, 1, figsize=(12, 10))
        ax = plt.axes(projection='3d')
        ax.scatter(points[:, 0], points[:, 1], points[:, 2], s=s)
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        plt.savefig('terrain_3d_plot.png', dpi=120)
        plt.show()
    