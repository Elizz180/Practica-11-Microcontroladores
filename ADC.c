#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/adc.h"

#define LM35_PIN        26      // GP26 = ADC0
#define ADC_INPUT       0       // ADC0
#define FAN_PIN         15      // GPIO para activar el transistor del ventilador
#define TEMP_UMBRAL     70.0f   // °C
#define VREF            3.3f    // Referencia ADC
#define ADC_MAX         4095.0f // 12 bits
#define SAMPLE_MS       500     // Tiempo entre muestras


int main() {
    stdio_init_all();
    sleep_ms(2000); // Da tiempo a que abra el monitor serial

    // Configuración del pin que controla el ventilador
    gpio_init(FAN_PIN);
    gpio_set_dir(FAN_PIN, GPIO_OUT);
    gpio_put(FAN_PIN, 0);

    // Inicialización del ADC
    adc_init();
    adc_gpio_init(LM35_PIN);   // Habilita GP26 como entrada analógica
    adc_select_input(ADC_INPUT);

    printf("Sistema iniciado\n");
    printf("LM35 en GP26 (ADC0)\n");
    printf("Control de ventilador en GP%d\n\n", FAN_PIN);

    while (true) {
        // 1) Leer ADC
        uint16_t raw = adc_read();

        // 2) Convertir a voltaje
        float voltaje = ((float)raw * VREF) / ADC_MAX;

        // 3) Convertir a temperatura (LM35 = 10 mV/°C)
        float temperatura_c = voltaje * 100.0f;

        // 4) Control del ventilador
        bool fan_on = (temperatura_c > TEMP_UMBRAL);
        gpio_put(FAN_PIN, fan_on);

        // 5) Enviar datos por USB serial
        printf("Temperatura: %.2f C | Voltaje: %.3f V | ADC: %u | Ventilador: %s\n",
               temperatura_c,
               voltaje,
               raw,
               fan_on ? "ENCENDIDO" : "APAGADO");

        sleep_ms(SAMPLE_MS);
    }

    return 0;
}
