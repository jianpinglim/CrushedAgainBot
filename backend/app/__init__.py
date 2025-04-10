from flask import Flask
import debugpy
import logging
import os
from .main_controller import MainController
 
logger = logging.getLogger(__name__)
 
 
class AppFactory:
    def __init__(self, settings):
        self._setup_logging()
 
        self._app = Flask(__name__)
        self._app.config.from_pyfile("config.cfg")
 
        self._main_controller = MainController(self._app)
        self._settings = settings
 
    @property
    def app(self):
        return self._app
 
    @property
    def main_controller(self):
        return self._main_controller
 
    def _setup_logging(self):
        log_dir = os.path.dirname(os.path.abspath(__file__))
        log_file = os.path.join(log_dir, "app.log")
 
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
 
    def _run_debugger(self):
        # Setup for VS Code debugger if required.
        if self._settings["should_debug"]:
            # Port 5679 for debugging
            debugpy.listen(("0.0.0.0", 5679))
            logger.info("Waiting for debugger attach...")
            debugpy.wait_for_client()
 
    def _print_app_configs(self):
        # Print the app configs if required.
        if self._settings["should_print_app_configs"]:
            logger.info("Loaded configuration:")
 
            for key, value in self._app.config.items():
                print(f"{key}: {value}")
 
    def run(self):
        self._run_debugger()
        self._print_app_configs()
 
        self._main_controller.run()
 
        return self._app
 
 
settings = {"should_debug": False, "should_print_app_configs": True}
 
app_factory = AppFactory(settings)
 
# The Flask App needs to be exposed for the Flask CLI to find it.
app = app_factory.run()