/* AI-assisted day-one build/flash/serial check; no wiring required. */
#include <inttypes.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"

void app_main(void)
{
    uint32_t seq = 0;
    while (1) {
        ESP_LOGI("smoke_test", "ESP32 running; heartbeat=%" PRIu32, seq++);
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
