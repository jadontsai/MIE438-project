#ifndef COMMANDS_H
#define COMMANDS_H

#include <stdint.h>

typedef struct
{
    int16_t steer;       // -100 to 100
    uint8_t speed;       // 0 to 100
    uint8_t catch_cmd;   // 0 or 1
    uint32_t last_rx_ms; // HAL_GetTick() timestamp
    uint8_t valid;
} AppCommand_t;

extern volatile AppCommand_t g_cmd;

void AppCmd_Reset(void);
void AppCmd_ParseBytes(const uint8_t *data, uint16_t len, uint32_t now_ms);

#endif
