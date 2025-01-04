import logging

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,  # Set the lowest severity level you want to log
    format='%(asctime)s - %(levelname)s - %(message)s',  # Define the log message format
    handlers=[
        logging.StreamHandler(),  # Log messages to console
        logging.FileHandler('app.log')  # Optionally, log messages to a file
    ]
)

# Define a custom logger (optional)
logger = logging.getLogger(__name__)

# Example of different log levels
def log_example():
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
