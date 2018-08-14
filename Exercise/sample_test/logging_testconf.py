import logging
import sys
import logging.config
import yaml


class NoParsingFilter(logging.Filter):
    def filter(self, record):
        return not record.getMessage().startswith('critical')


#logging.config.fileConfig('logging.conf')
# Loading config. Of course this is in another file in the real life
with open('logging_conf', 'r') as f:
    config = yaml.safe_load(f.read())
logging.config.dictConfig(config)

# create logger
logger = logging.getLogger('simpleExample')
#logger = logging.getLogger(__name__)

logger.addFilter(NoParsingFilter())

# 'application' code
logger.debug('debug message')
logger.info('info message')
logger.warning('warn message')
logger.error('error message')
logger.critical('critical message')