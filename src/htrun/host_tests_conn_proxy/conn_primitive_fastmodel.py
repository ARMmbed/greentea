#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Connect to fast models."""

from .conn_primitive import ConnectorPrimitive, ConnectorPrimitiveException


class FastmodelConnectorPrimitive(ConnectorPrimitive):
    """ConnectorPrimitive for a FastModel.

    Wrapper around fm_agent module.
    """

    def __init__(self, name, config):
        """Initialise the FastModel.

        Args:
            name: Name of the FastModel.
            config: Map of config parameters describing the state of the FastModel.
        """
        ConnectorPrimitive.__init__(self, name)
        self.config = config
        self.fm_config = config.get("fm_config", None)
        self.platform_name = config.get("platform_name", None)
        self.image_path = config.get("image_path", None)
        self.polling_timeout = int(config.get("polling_timeout", 60))

        # FastModel Agent tool-kit
        self.fm_agent_module = None
        self.resource = None

        # Initialize FastModel
        if self.__fastmodel_init():

            # FastModel Launch load and run, equivalent to DUT connection, flashing and
            # reset...
            self.__fastmodel_launch()
            self.__fastmodel_load(self.image_path)
            self.__fastmodel_run()

    def __fastmodel_init(self):
        """Import the fm_agent module and set up the FastModel simulator.

        Raises:
            ConnectorPrimitiveException: fm_agent import failed, or the FastModel setup
                failed.
        """
        self.logger.prn_inf("Initializing FastModel...")

        try:
            self.fm_agent_module = __import__("fm_agent")
        except ImportError as e:
            self.logger.prn_err(
                "unable to load mbed-fastmodel-agent module. Check if the module "
                "install correctly."
            )
            self.fm_agent_module = None
            self.logger.prn_err("Importing failed : %s" % str(e))
            raise ConnectorPrimitiveException("Importing failed : %s" % str(e))
        try:
            self.resource = self.fm_agent_module.FastmodelAgent(logger=self.logger)
            self.resource.setup_simulator(self.platform_name, self.fm_config)
            if self.__resource_allocated():
                pass
        except self.fm_agent_module.SimulatorError as e:
            self.logger.prn_err("module fm_agent, create() failed: %s" % str(e))
            raise ConnectorPrimitiveException(
                "FastModel Initializing failed as throw SimulatorError!"
            )

        return True

    def __fastmodel_launch(self):
        """Start the FastModel.

        Raises:
            ConnectorPrimitiveException: Simulator start-up failed.
        """
        self.logger.prn_inf("Launching FastModel...")
        try:
            if not self.resource.start_simulator():
                raise ConnectorPrimitiveException(
                    "FastModel running failed, run_simulator() return False!"
                )
        except self.fm_agent_module.SimulatorError as e:
            self.logger.prn_err("start_simulator() failed: %s" % str(e))
            raise ConnectorPrimitiveException(
                "FastModel launching failed as throw FastModelError!"
            )

    def __fastmodel_run(self):
        """Run the FastModel simulator.

        Raises:
            ConnectorPrimitiveException: Failed to run the simulator.
        """
        self.logger.prn_inf("Running FastModel...")
        try:
            if not self.resource.run_simulator():
                raise ConnectorPrimitiveException(
                    "FastModel running failed, run_simulator() return False!"
                )
        except self.fm_agent_module.SimulatorError as e:
            self.logger.prn_err("run_simulator() failed: %s" % str(e))
            raise ConnectorPrimitiveException(
                "FastModel running failed as throw SimulatorError!"
            )

    def __fastmodel_load(self, filename):
        """Load a firmware image to the FastModel.

        This is the functional equivalent of flashing a physical DUT.

        Args:
            filename: Path to the image to load.
        """
        self.logger.prn_inf("loading FastModel with image '%s'..." % filename)
        try:
            if not self.resource.load_simulator(filename):
                raise ConnectorPrimitiveException(
                    "FastModel loading failed, load_simulator() return False!"
                )
        except self.fm_agent_module.SimulatorError as e:
            self.logger.prn_err("run_simulator() failed: %s" % str(e))
            raise ConnectorPrimitiveException(
                "FastModel loading failed as throw SimulatorError!"
            )

    def __resource_allocated(self):
        """Check if the FastModel agent resource been 'allocated'.

        Returns:
            True if the FastModel agent is available.
        """
        if self.resource:
            return True
        else:
            self.logger.prn_err("FastModel resource not available!")
            return False

    def read(self, count):
        """Read data from the FastModel.

        Args:
            count: Not used for FastModels.

        Returns:
            The data from the FastModel if the read was successful, otherwise False.
        """
        if not self.__resource_allocated():
            return False

        try:
            return self.resource.read()
        except self.fm_agent_module.SimulatorError as e:
            self.logger.prn_err(
                "FastmodelConnectorPrimitive.read() failed: %s" % str(e)
            )

    def write(self, payload, log=False):
        """Send text to the FastModel.

        Args:
            payload: Text to send to the FastModel.
            log: Log the text payload if True.
        """
        if self.__resource_allocated():
            if log:
                self.logger.prn_txd(payload)
            try:
                self.resource.write(payload)
            except self.fm_agent_module.SimulatorError as e:
                self.logger.prn_err(
                    "FastmodelConnectorPrimitive.write() failed: %s" % str(e)
                )
            else:
                return True
        else:
            return False

    def flush(self):
        """Flush is not supported in the FastModel_module."""
        pass

    def connected(self):
        """Check if the FastModel is running."""
        if self.__resource_allocated():
            return self.resource.is_simulator_alive
        else:
            return False

    def finish(self):
        """Shut down the FastModel."""
        if self.__resource_allocated():
            try:
                self.resource.shutdown_simulator()
                self.resource = None
            except self.fm_agent_module.SimulatorError as e:
                self.logger.prn_err(
                    "FastmodelConnectorPrimitive.finish() failed: %s" % str(e)
                )

    def reset(self):
        """Reset the FastModel."""
        if self.__resource_allocated():
            try:
                if not self.resource.reset_simulator():
                    self.logger.prn_err(
                        "FastModel reset failed, reset_simulator() return False!"
                    )
            except self.fm_agent_module.SimulatorError as e:
                self.logger.prn_err(
                    "FastmodelConnectorPrimitive.reset() failed: %s" % str(e)
                )

    def __del__(self):
        """Shut down the FastModel when garbage collected."""
        self.finish()
