# OpticalControlSystem

## Getting started
This repository contains the API based on QCoDeS to operate the QphoX Optical Control System.
 
 
## Installation
- Clone the repository and navigate to the ```qx_ocs``` folder
- Double click on ```create_qphoxvenv.bat``` to initialise the conda virtual environment
- Follow sections 2.2 and 3.1 of the Application Note to use the software
 
## Library Usage
The OpticalControlSystem class is accessed via an IP address and can be operated using parameters and functions explained below.

## List of parameters 
| Parameter               | Getter | Setter | Inputs (if applicable)                   |
| :---------------------: | :----: | :----: | :--------------------------------------: |
| ```IP```                | Yes    | Yes    | ```192.168.1.1``` to ```192.168.1.127``` |
| ```laser_output```      | Yes    | Yes    | ```on``` or ```off```                    |
| ```laser_switch```      | Yes    | Yes    | ```internal``` or ```external```         |
| ```laser_attenuation``` | Yes    | Yes    | ```0``` to ```35``` dB                   |
| ```attenuator_power```  | Yes    | No     | N.A                                      |
| ```eom_setpoint```      | Yes    | No     | N.A                                      |
| ```eom_voltage```       | Yes    | No     | N.A                                      |
| ```modulator_power```   | Yes    | No     | N.A                                      |
| ```output_power```      | Yes    | No     | N.A                                      |
| ```output_switch```     | Yes    | Yes    | ```0``` to ```8```                       |


## Important functions
- set_output_power
 
        Input: required_output_power
        Optional Inputs: laser_attenuation, power_correction_factor
        Set an optical power at the enabled output channel in Watt
 
- auto_tune_up
 
        Input: maximize_polarization, eom_setpoint, eom_resolution, eom_plot
        Default: 5V
        Optimize the light polarization and the EOM to the null/quadrature point of its voltage bias curve

- start_output_power_stabilisation

        Optional Inputs: k_p, k_i, k_d, averaging_time, sample_time
        Spawn a background thread to stabilise the output power
 
- stop_output_power_stabilisation

        Output: result_dict
        Terminate the output power stabilisation and obtain the accumulated dictionary of results
 
 
## Support and maintenance
 
In case of maintenance or service inquiries, please contact us at:

    Address: Elektronicaweg 10, 2628XG, Delft, The Netherlands
    Email: info@qphox.eu


