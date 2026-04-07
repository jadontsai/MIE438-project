#ifndef PID_H
#define PID_H

/*
Header file defining the function implementing a simple proportional-integral-derivative 
(PID) control loop. 

Also contains a variety of volatile variables shared between p2p_server_app.c
and main.c. These variables are initialized here as this header file is referenced
in both programs.
*/

/*
Variable used in p2p_server_app.c and main.c, to signal whether a new value has been 
received over BLE (which would trigger the PID to update).
*/ 
extern volatile int new_value_flag;

/*
Variable used in p2p_server_app.c and main.c, which contains the value of the bounding
box width received over BLE.
*/
extern volatile int width;

/*
Variable used in p2p_server_app.c and main.c, which contains the value of the angular 
difference to the center of the box received over BLE.
*/
extern volatile int angular_error;

#include <stdint.h>

/*
The function used to calculate the resulting output, integral and error values for a single
PID update loop. 
*/
int pid_update(int error, float dt, float kp, float ki, float kd, int *integral, int *prev_error, int integral_limit, int output_limit);


#endif