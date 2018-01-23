# University of the West of Scotland
# Author: Guillermo Siesto Sanchez B00334584
# Date: 2018
# Description: The purpose of this coursework is to develop a distributed chat system using a networking library.

# ===========
# C L I E N T
# ===========

# Imports
import logging # Generate a log file to record all the changes made

# Config
logging.basicConfig(level=logging.INFO, filename='log/ChatApplication_client.log', format='[%(levelname)s] %(asctime)s %(message)s', )


# Inicialization
free = true
kick = false
grant = 1 # 0 = Superuser ; 1 = Normaluser
