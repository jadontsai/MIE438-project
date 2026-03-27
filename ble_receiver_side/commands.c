#include "commands.h"
#include <stdio.h>
#include <string.h>

volatile AppCommand_t g_cmd = {0};

void AppCmd_Reset(void)
{
    g_cmd.steer = 0;
    g_cmd.speed = 0;
    g_cmd.catch_cmd = 0;
    g_cmd.last_rx_ms = 0;
    g_cmd.valid = 0;
}

static int clamp_int(int value, int lo, int hi)
{
    if (value < lo) return lo;
    if (value > hi) return hi;
    return value;
}

void AppCmd_ParseBytes(const uint8_t *data, uint16_t len, uint32_t now_ms)
{
    char buf[32];
    int steer = 0;
    int speed = 0;
    int catch_cmd = 0;

    if (data == NULL || len == 0) return;

    if (len >= sizeof(buf))
        len = sizeof(buf) - 1;

    memcpy(buf, data, len);
    buf[len] = '\0';

    // Expected format: "steer,speed,catch\n"
    if (sscanf(buf, "%d,%d,%d", &steer, &speed, &catch_cmd) == 3)
    {
        steer = clamp_int(steer, -100, 100);
        speed = clamp_int(speed, 0, 100);
        catch_cmd = catch_cmd ? 1 : 0;

        g_cmd.steer = (int16_t)steer;
        g_cmd.speed = (uint8_t)speed;
        g_cmd.catch_cmd = (uint8_t)catch_cmd;
        g_cmd.last_rx_ms = now_ms;
        g_cmd.valid = 1;
    }
}
