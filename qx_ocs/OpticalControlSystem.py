import time
import sys
import os

try:
    from .src.OpticalControlSystemInstrument import OpticalControlSystemInstrument
    from .src import parameters as param
except ImportError:
    from src.OpticalControlSystemInstrument import OpticalControlSystemInstrument
    from src import parameters as param
    
class OpticalControlSystem(OpticalControlSystemInstrument):

    def __init__(self, name, address, debug=False, **kwargs):

        super().__init__(name, address, debug, **kwargs)

        super().add_parameter(param.IP, get_cmd=super().get_IP, set_cmd=super().set_IP)

        super().add_parameter(param.output_switch, get_cmd=super().get_output_switch, set_cmd=super().set_output_switch)

        super().add_parameter(param.laser_output, get_cmd=super().get_laser_output, set_cmd=super().set_laser_output)

        super().add_parameter(param.laser_switch, get_cmd=super().get_laser_switch, set_cmd=super().set_laser_switch)

        super().add_parameter(param.laser_attenuation, get_cmd=super().get_laser_attenuation, set_cmd=super().set_laser_attenuation)

        super().add_parameter(param.attenuator_power, get_cmd=super().get_attenuator_power, set_cmd=None)

        super().add_parameter(param.modulator_power, get_cmd=super().get_modulator_power, set_cmd=None)

        super().add_parameter(param.eom_setpoint, get_cmd=super().get_eom_setpoint, set_cmd=None)

        super().add_parameter(param.eom_voltage, get_cmd=super().get_eom_voltage, set_cmd=None)

        super().add_parameter(param.output_power, get_cmd=super().get_output_power, set_cmd=None)
        
        super().initialize()

    def __del__(self):
        super().__del__()

    def close(self):
        super().close()

    def auto_tune_up(self, maximize_polarization=False, eom_setpoint='midpoint', eom_resolution=0.25, eom_plot=False):
        super().auto_tune_up(maximize_polarization=maximize_polarization, eom_setpoint=eom_setpoint, eom_resolution=eom_resolution, eom_plot=eom_plot)