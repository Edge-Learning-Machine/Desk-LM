# https://stackoverflow.com/questions/11548674/logging-info-doesnt-show-up-on-console-but-warn-and-error-do/11548754
# https://realpython.com/python-logging/
import os

import logging

logger = 0

def initLogger(dataset, algo):
    global logger
    # Create a custom logger
    logger = logging.getLogger(__name__)

    if os.path.isdir('./log/') == False:
        os.mkdir('./log/')
    
    # set up logging to file
    logging.basicConfig(level=logging.INFO,
                        #format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        format='%(asctime)s %(message)s',
                        datefmt='%d/%m/%y %H:%M:%S',
                        filename=f'./log/{dataset}.log',
                        filemode='a')
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)

    #logger.warning('This is a warning')
    #logger.error('This is an error')
    logger.info(f'Dataset: {dataset}, algorithm: {algo}')