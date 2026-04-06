#ifndef PID_H
#define PID_H

extern volatile int new_value_flag;
extern volatile int width;
extern volatile int angular_error;

#include <stdint.h>

typedef struct
{
    float kp;
    float ki;
    float kd;

    uint16_t integral;
    uint16_t prev_error;
    uint16_t integral_limit;
    uint16_t output_limit;
    uint8_t initialized;
} PID_Controller_t;

void PID_Init(PID_Controller_t *pid, float kp, float ki, float kd, uint16_t integral_limit, uint16_t output_limit);
void PID_Reset(PID_Controller_t *pid);
int PID_Update(PID_Controller_t *pid, int error, float dt);





#endif