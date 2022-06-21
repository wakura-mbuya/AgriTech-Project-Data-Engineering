# AgriTech-Project (Data Engineering)

## Project Overview
At AgriTech, understanding how water flows through a maize farm field is key. This knowledge will help them improve their research on new agricultural products being tested on the farms. How much maize a field produces is very spatially variable. Even if the same farming practices, seeds and fertilizer are applied exactly the same by machinery over a field, there can be a very large harvest at one corner and a low harvest at another corner.  AgriTech would like to be able to better understand which parts of the farm are likely to produce more or less maize, so that if they try a new fertilizer on part of this farm, they would have more confidence that any differences in the maize harvest are due mostly to the new fertilizer changes, and not just random effects due to other environmental factors. 

Water is very important for crop growth and health.  AgriTech can better predict maize harvest if they better understand how water flows through a field, and which parts are likely to be flooded or too dry. One important ingredient to understanding water flow in a field is by measuring the elevation of the field at many points. The USGS recently released high resolution elevation data as a lidar point cloud called USGS 3DEP in a public dataset on Amazon. This dataset is essential to build models of water flow and predict plant health and maize harvest. 

The objective this project is to produce an easy to use, reliable and well designed python module that domain experts and data scientists can use to fetch, visualise, and transform publicly available satellite and LIDAR data. In particular, the code should interface with USGS 3DEP and fetch data using the USGS API.

## Project Objective
The objective this project is to produce an easy to use, reliable and well designed python module that domain experts and data scientists can use to fetch, visualise, and transform publicly available satellite and LIDAR data. In particular, the code should interface with USGS 3DEP and fetch data using the USGS API.
