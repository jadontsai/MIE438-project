
#include "pid.h"
#include <stdint.h>

volatile int new_value_flag = 0;
volatile int width = 0;
volatile int angular_error = 0;

static int clamp(int x, int lo, int hi)
{
    if (x < lo) return lo;
    if (x > hi) return hi;
    return x;
}

void PID_Init(PID_Controller_t *pid, float kp, float ki, float kd, uint16_t integral_limit, uint16_t output_limit)
{
    pid->kp = kp;
    pid->ki = ki;
    pid->kd = kd;
    pid->integral = 0;
    pid->prev_error = 0;
    pid->integral_limit = integral_limit;
    pid->output_limit = output_limit;
    pid->initialized = 0;
}

void PID_Reset(PID_Controller_t *pid)
{
    pid->integral = 0;
    pid->prev_error = 0;
    pid->initialized = 0;
}

int PID_Update(PID_Controller_t *pid, int error, float dt)
{
    int derivative;
    int output;

    if (dt <= 0)
    {
        return 0;
    }

    if (!pid->initialized)
    {
        pid->prev_error = error;
        pid->initialized = 1;
    }

    pid->integral += error * dt;
    pid->integral = clamp(pid->integral, -1*pid->integral_limit, pid->integral_limit);
    derivative = (error - pid->prev_error) / dt;

    output = pid->kp * error + pid->ki * pid->integral + pid->kd * derivative;
    output = clamp(output, -1*pid->output_limit, pid->output_limit);

    pid->prev_error = error;
    return output;
}

