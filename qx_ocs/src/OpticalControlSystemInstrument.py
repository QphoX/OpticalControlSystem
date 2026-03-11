import qcodes

import os

from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import threading
import time

import csv
import stat

try:
    from .qx_ocs_core.PDC_main import Labphox_PDC
except ImportError:
    from qx_ocs_core.PDC_main import Labphox_PDC
    

class OpticalControlSystemInstrument(qcodes.Instrument):
    
    def __init__(self, name, address, debug=False, **kwargs):
        super().__init__(name, **kwargs)

        self.debug = debug
        
        self.__pdc = Labphox_PDC(IP=address, debug=debug)
        self.__pdc.connect()

    def initialize(self):
        print(f"OpticalControlSystem '{self.name}' | Initializing device {self.IP.get()}")

        self.output_switch.set(0)
        time.sleep(0.5)
        print(f"OpticalControlSystem '{self.name}' | Output switch: {self.output_switch.get()}")

        self.laser_output.set('on')
        time.sleep(0.5)
        print(f"OpticalControlSystem '{self.name}' | Laser output: {self.laser_output.get()}")

        self.laser_switch.set('internal')
        time.sleep(0.5)
        print(f"OpticalControlSystem '{self.name}' | Laser switch: {self.laser_switch.get()}")

        self.__pdc.set_VOA1_mode('man')
        self.__pdc.set_VOA1_att(0)

        self.laser_attenuation.set(0)
        time.sleep(0.5)
        print(f"OpticalControlSystem '{self.name}' | Laser attenuation: {self.laser_attenuation.get()} dB")

        self.auto_tune_up()

        print(f"OpticalControlSystem '{self.name}' | EOM setpoint: {self.eom_setpoint.get()}")

        print(f"OpticalControlSystem '{self.name}' | EOM voltage: {self.eom_voltage.get():.2e} V")

        print(f"OpticalControlSystem '{self.name}' | Attenuator power: {self.attenuator_power.get():.2e} W")

        print(f"OpticalControlSystem '{self.name}' | Modulator power: {self.modulator_power.get():.2e} W")

        print(f"OpticalControlSystem '{self.name}' | Output power: {self.output_power.get():.2e} W")

        if self.debug:
            print(f"OpticalControlSystem '{self.name}' | Parameter snapshot")
            print(self.print_readable_snapshot())

        self.__initialize_logger()

    def __del__(self):
        self.close()

    def close(self):
        print(f"OpticalControlSystem '{self.name}' | Closing device {self.IP.get()}")

        # Signal the thread to stop
        self.__stop_logging.set()
        self.__logger_thread.join()
        print(f"OpticalControlSystem '{self.name}' | Logging stopped and file saved.")
        
        self.output_switch.set(0)
        time.sleep(0.5)
        print(f"OpticalControlSystem '{self.name}' | Output switch: {self.output_switch.get()}")

        self.laser_output.set('off')
        time.sleep(0.5)
        print(f"OpticalControlSystem '{self.name}' | Laser output: {self.laser_output.get()}")

        self.laser_switch.set('internal')
        time.sleep(0.5)
        print(f"OpticalControlSystem '{self.name}' | Laser switch: {self.laser_switch.get()}")

        self.__pdc.set_VOA1_mode('man')
        self.__pdc.set_VOA1_att(0)

        self.laser_attenuation.set(0)
        time.sleep(0.5)
        print(f"OpticalControlSystem '{self.name}' | Laser attenuation: {self.laser_attenuation.get()} dB")

        print(f"OpticalControlSystem '{self.name}' | EOM voltage: {self.eom_voltage.get():.2e} V")

        print(f"OpticalControlSystem '{self.name}' | Attenuator power: {self.attenuator_power.get():.2e} W")

        print(f"OpticalControlSystem '{self.name}' | Modulator power: {self.modulator_power.get():.2e} W")

        print(f"OpticalControlSystem '{self.name}' | Output power: {self.output_power.get():.2e} W")

        if self.debug:
            print(f"OpticalControlSystem '{self.name}' | Parameter snapshot")
            print(self.print_readable_snapshot())
            
        super().close()

    def set_IP(self, value):
        self.__pdc.set_ip(value)

    def get_IP(self):
        return self.__pdc.get_ip()

    def set_output_switch(self, value):
        self.__pdc.set_output_switchN(value)

    def get_output_switch(self):
        return self.__pdc.get_output_switchN()

    def set_laser_output(self, value):
        self.__set_laser_output(value)

    def get_laser_output(self):
        return self.__pdc.laser_pl_get_status()

    def set_laser_switch(self, value):
        self.__pdc.set_switch(value)

    def get_laser_switch(self):
        return self.__pdc.get_laser_switch()

    def set_laser_attenuation(self, value):
        self.__pdc.set_VOA2_att(value)

    def get_laser_attenuation(self):
        return self.__pdc.get_VOA2_att()

    def get_attenuator_power(self):
        return self.__pdc.get_OPPower_avg(channel=0, averages=5)["avg"]

    def get_modulator_power(self):
        return self.__pdc.get_OPPower_avg(channel=1, averages=5)["avg"]

    def get_output_power(self):
        return self.__pdc.get_OPPower_avg(channel=2, averages=5)["avg"]

    def set_output_power(self, required_output_power, laser_attenuation=None, power_correction_factor=1.0):
        converged_to_required_power = self.__pdc.set_output_power(required_output_power=required_output_power, voa2_attenuation=laser_attenuation, power_correction_factor=power_correction_factor)
        if not converged_to_required_power:
            print(f"OpticalControlSystem '{self.name}' | Could not set required output power. \
                Consider changing laser attenuation and power correction factor manually.")
   
    def start_output_power_stabilisation(self, k_p=0.24, k_i=0.05, k_d=0.12, averaging_time=0.2, sample_time=1.5):
        self.__pdc.start_output_power_stabilisation(k_p=k_p, k_i=k_i, k_d=k_d, averaging_time=averaging_time, sample_time=sample_time)

    def stop_output_power_stabilisation(self):
        result = self.__pdc.stop_output_power_stabilisation()
        return result

    def get_eom_setpoint(self):
        return self.__eom_setpoint

    def get_eom_voltage(self):
        return self.__pdc.get_EOM_voltage()

    def get_UIDs(self):
        return self.__pdc.get_UIDs()

    def auto_tune_up(self, maximize_polarization=False, eom_setpoint='midpoint', eom_resolution=0.25, eom_plot=False):
        print(f"OpticalControlSystem '{self.name}' | Auto tune-up | Saving current parameters")
        current_output_switchN = self.output_switch.get()
        current_laser_attenuation = self.laser_attenuation.get()
        current_voa1_mode = self.__pdc.get_VOA1_mode()
        if current_voa1_mode == 'MANUAL':
            current_voa1_attenuation = self.__pdc.get_VOA1_att()
        else:
            current_attenuator_power = self.attenuator_power.get()

        print(f"OpticalControlSystem '{self.name}' | Auto tune-up | Disabling output")
        self.output_switch.set(0)

        if maximize_polarization:
            self.__maximize_polarization()

        if 'mid' in eom_setpoint.lower():
            self.__eom_setpoint, self.__eom_voltage = self.__find_EOM_midpoint(resolution=eom_resolution, plot=eom_plot)
        elif 'min' in eom_setpoint.lower():
            self.__eom_setpoint, self.__eom_voltage = self.__find_EOM_minpoint(resolution=eom_resolution, plot=eom_plot)
        elif 'max' in eom_setpoint.lower():
            self.__eom_setpoint, self.__eom_voltage = self.__find_EOM_maxpoint(resolution=eom_resolution, plot=eom_plot)
        else:
            self.__eom_setpoint = eom_setpoint + " (INVALID)"
            self.__eom_voltage = None
            print(f"OpticalControlSystem '{self.name}' | Auto tune-up | Invalid EOM setpoint '{eom_setpoint}'. Try 'midpoint', 'minpoint', or 'maxpoint'.")
        
        if "INVALID" not in self.__eom_setpoint and self.__eom_voltage is not None:
            self.__pdc.set_EOM_voltage(voltage = self.__eom_voltage)
            print(f"OpticalControlSystem '{self.name}' | Auto tune-up | EOM setpoint '{self.eom_setpoint.get()}' reached at {self.eom_voltage.get():.2e} V")

        if self.debug:
            print(f"OpticalControlSystem '{self.name}' | Parameter snapshot")
            print(self.print_readable_snapshot())

        print(f"OpticalControlSystem '{self.name}' | Auto tune-up | Restoring current parameters")
        self.output_switch.set(current_output_switchN)
        self.laser_attenuation.set(current_laser_attenuation)
        self.__pdc.set_VOA1_mode(current_voa1_mode)
        if current_voa1_mode == 'MANUAL':
            self.__pdc.set_VOA1_att(current_voa1_attenuation)
        else:
            self.__pdc.set_OP_PM(current_attenuator_power)
        time.sleep(0.5)

        if self.debug:
            print(f"OpticalControlSystem '{self.name}' | Parameter snapshot")
            print(self.print_readable_snapshot())

    def plot_power_specs(self, result_dict, power_prefix):
        import numpy as np
        import matplotlib.pyplot as plt
        from scipy.stats import norm
        import os
        import json
        
        save_folder = 'output_power_specs/' + power_prefix
        save_prefix = save_folder + '/' + power_prefix + '_'
        os.makedirs(save_folder, exist_ok=True)
        
        timestamps_s = result_dict['timestamps_s']
        pm1_optical_powers = result_dict['pm1_optical_powers']
        pm1_optical_power_required = result_dict['pm1_optical_power_required']
        eom_voltages = result_dict['eom_voltages']
        output_channel = 'CH'+str(self.output_switch.get())

        def get_combined_labels(lines):
            return [line.get_label() for line in lines]
    
        plot_length = np.min((len(timestamps_s), len(pm1_optical_powers), len(eom_voltages)))
        
        pm1_optical_powers_norm = [pm1_optical_power/pm1_optical_power_required for pm1_optical_power in pm1_optical_powers]
        timestamps_h = [timestamp/3600 for timestamp in timestamps_s]
        
        fig1, ax1 = plt.subplots()
        ax1.set_xlabel('Time [h]')
        ax2 = ax1.twinx()
        ax1.axhline(1.0)
        line1 = ax1.plot(timestamps_h[:plot_length], pm1_optical_powers_norm[:plot_length],'-r', label='Normalized Optical Power')
        line2 = ax2.plot(timestamps_h[:plot_length], eom_voltages[:plot_length],'-b', label='EOM Bias Voltage')
        ax1.set_ylabel('Normalized Optical power [-]')
        ax2.set_ylabel('EOM bias voltage [V]')
        ax1.grid()
        lines=line1+line2
        ax1.legend(lines,get_combined_labels(lines),loc='best')
        fig1.tight_layout()
        fig1.show()
        fig1.savefig(save_prefix+"Normalized_Optical_Power_TimeSeries")

        mean_pm1_optical_power_norm = np.mean(pm1_optical_powers_norm)
        std_pm1_optical_power_norm = np.std(pm1_optical_powers_norm)
        x_pm1 = np.linspace(min(pm1_optical_powers_norm), max(pm1_optical_powers_norm), 1000000)
        y_pm1 = norm.pdf(x_pm1, mean_pm1_optical_power_norm, std_pm1_optical_power_norm)
        fig2, ax2 = plt.subplots()
        ax2.plot(x_pm1, y_pm1, label='Normal distribution')
        ax2.hist(pm1_optical_powers_norm, bins=30, density=True, alpha=0.6, color='g', label='Histogram')
        ax2.text(mean_pm1_optical_power_norm, max(y_pm1)*0.1, f'Mean: {mean_pm1_optical_power_norm:.4e}\nStd: {std_pm1_optical_power_norm:.4e}', horizontalalignment='center', verticalalignment='center',fontsize=12, color='k')
        ax2.set_xlabel('Normalized Optical Power [-]')
        ax2.set_ylabel('Probability Density')
        ax2.grid()
        ax2.legend(loc='best')
        fig2.tight_layout()
        fig2.show()
        fig2.savefig(save_prefix+"Normalized_Optical_Power_ProbabilityDistribution")

        result_dict['pm1_optical_powers_normalized'] = pm1_optical_powers_norm
        result_dict['pm1_optical_powers_normalized_mean'] = mean_pm1_optical_power_norm
        result_dict['pm1_optical_powers_normalized_std'] = std_pm1_optical_power_norm

        result_dict_sorted = {k: result_dict[k] for k in sorted(result_dict)}

        with open(save_prefix+"results.json", "w") as f:
            json.dump(result_dict_sorted, f, indent=4)

        print(f"OpticalControlSystem '{self.name}' | Saved power stability results to '{save_folder}'")
    
    def __set_laser_output(self, mode='off'):
        if mode.lower() == 'on':
            self.__pdc.laser_pl_on()
        else:
            self.__pdc.laser_pl_off()

    def __maximize_polarization(self):
        print(f"OpticalControlSystem '{self.name}' | Maximizing polarization")
        return self.__pdc.maximize_polarization()

    def __find_EOM_midpoint(self, resolution=0.025, plot=False):
        print(f"OpticalControlSystem '{self.name}' | Finding EOM midpoint")
        eom_midpoint = self.__pdc.find_EOM_midpoint(resolution=resolution, plot=plot)
        print(f"OpticalControlSystem '{self.name}' | EOM midpoint: {eom_midpoint:.2e} V")
        return ['MID', eom_midpoint]

    def __find_EOM_minpoint(self, resolution=0.025, plot=False):
        print(f"OpticalControlSystem '{self.name}' | Finding EOM minpoint")
        eom_minpoint = self.__pdc.find_EOM_minpoint(resolution=resolution, plot=plot)
        print(f"OpticalControlSystem '{self.name}' | EOM minpoint: {eom_minpoint:.1e} V")
        return ['MIN', eom_minpoint]

    def __find_EOM_maxpoint(self, resolution=0.025, plot=False):
        print(f"OpticalControlSystem '{self.name}' | Finding EOM maxpoint")
        eom_maxpoint = self.__pdc.find_EOM_maxpoint(resolution=resolution, plot=plot)
        print(f"OpticalControlSystem '{self.name}' | EOM maxpoint: {eom_maxpoint:.1e} V")
        return ['MAX', eom_maxpoint]

    def snapshot(self, update=True, params_to_update=None):
        if update:
            for name, param in self.parameters.items():
                if name.upper() == 'IDN' : continue
                try:
                    param.get()
                except Exception as e:
                    print(f"OpticalControlSystem '{self.name}' | Warning: could not get {name}: {e}")
        return super().snapshot(update=False)

    def print_readable_snapshot(self, update=True):
        self.snapshot(update=update)
        super().print_readable_snapshot(update=False)

    def __initialize_logger(self):
        self.__log_interval = 30  # in seconds
        self.__stop_logging = threading.Event()

        # Start background logger thread
        self.__logger_thread = threading.Thread(target=self.__log_loop, daemon=True)
        self.__logger_thread.start()
        if self.debug:
            print(f"OpticalControlSystem '{self.name}' | Logging started every {self.__log_interval} seconds.")

    def __log_loop(self):
        while not self.__stop_logging.is_set():
            self.__save_snapshot_to_readonly_logs()
            time.sleep(self.__log_interval)

    def __get_filename(self):
        """Generate a unique filename for this instrument per day."""
        # Get current date in yyyy_mm_dd format
        date_str = datetime.now().strftime('%Y_%m_%d')
        return f"{date_str}_logs_{self.name}.csv"

    def __save_snapshot_to_readonly_logs(self):
        logs_folder = "logs"
        if not os.path.exists(logs_folder):
            os.makedirs(logs_folder)

        filename = os.path.join(logs_folder, self.__get_filename())
        snapshot = self.snapshot()
        time_str = datetime.now().strftime('%H:%M:%S')

        # Extract parameter names and values from snapshot, excluding IDN
        param_names = [
            param for param in snapshot['parameters']
            if param.upper() != 'IDN'
        ]
        row = [time_str]
        for param in param_names:
            value = snapshot['parameters'][param].get('value', '<missing>')
            row.append(value)

        file_exists = os.path.exists(filename)

        if file_exists:
            os.chmod(filename, stat.S_IWRITE)

        with open(filename, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['Time'] + param_names)
            writer.writerow(row)

        os.chmod(filename, stat.S_IREAD)

        if self.debug:
            print(f"Snapshot appended to {filename} (now read-only)")
