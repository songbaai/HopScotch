Require Python version 3.x

All scripts were run locally, as we had issues utilizing the cluster for our needs. Configuring the proper environment for Python was a hassle due to limited sudo privileges. While it was possible to install most libraries it could only be done as user.

This created issues because some notable libraries required an updated pip installation, and the provided pip version was not upgradable from a user level. Emailing with IT staff did not solve the situation easily. This is why we ended up relying largely on local machines to run our python scripts.

The order of scripts is as follows:

Yelp-scraper.py - reads in zip codes and to grab data and produce the resulting .json files

Clustering.py - takes in said .json and zip files and passes it’s data frame over for routing.

Routing.py - calculated proper paths and writes to most30.csv

Websocket.py - takes in the most30.csv and displays to gmapdirection.html.

You can view these results by opening said page in any modern browser with websocket.py running locally.

All required libraries are provided at the top of each script. 

They include: 

	py-spark
	gql
	sklearn
	matplotlib
	or tools
	pandas
	websockets
	asyncio

This is not an exhaustive list but the remainder should come with a standard Python installation.

