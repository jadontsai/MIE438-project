/*
Implementation of a simple proportional-integral-derivative (PID) control loop. 

The integral and output values are clamped to limit values set in main.c to ensure the 
output value does not exceed the maximum PWM duty cycle. 

Also contains a variety of volatile variables shared between 
*/


#include "pid.h"
#include <stdint.h>

/*
Variable used in p2p_server_app.c and main.c, to signal whether a new value has been 
received over BLE (which would trigger the PID to update).
*/ 
volatile int new_value_flag = 0;

/*
Variable used in p2p_server_app.c and main.c, which contains the value of the bounding
box width received over BLE.
*/
volatile int width = 0;

/*
Variable used in p2p_server_app.c and main.c, which contains the value of the angular 
difference to the center of the box received over BLE.
*/
volatile int angular_error = 0;


/*
Clamping function, used to limit the integral and output values calculated during the
PID update.
*/
static int clamp(int x, int lo, int hi)
{
    if (x < lo) return lo;
    if (x > hi) return hi;
    return x;
}


/*
The function used to calculate the resulting output, integral and error values for a single
PID update loop. 
*/
int pid_update(int error, float dt, float kp, float ki, float kd, int *integral, int *prev_error, int integral_limit, int output_limit)
{
    int derivative;
    int output;

    /*
    Calculate and clamp the integral and derivative values.
    */
    *integral += error*dt;
    *integral = clamp(*integral, -1*integral_limit, integral_limit);
    derivative = (error - *prev_error) / dt;

    /*
    Calculate and clamp the output value.
    */
    output = kp*error + ki*(*integral) + kd*derivative;
    output = clamp(output, -1*output_limit, output_limit);

    /*
    Set the value of the previous error for future loops, and return the output value.
    */
    *prev_error = error;
    return output;
}

