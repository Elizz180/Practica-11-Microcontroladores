cmake_minimum_required(VERSION 3.13)
# Nombre del proyecto
project(Practica_11)

# Habilitar la Raspberry Pi Pico SDK
include(pico_sdk_import.cmake)

set(PICO_BOARD pico_w)
pico_sdk_init()

# Agregar el archivo fuente
add_executable(ADC
    ADC.c
)

# Agregar las bibliotecas estándar de la Pico
target_link_libraries(ADC
    pico_stdlib
    hardware_adc
)

# Habilitar la salida USB para el puerto serie
pico_enable_stdio_usb(ADC 1)
pico_enable_stdio_uart(ADC 0)

# Crear el archivo binario UF2
pico_add_extra_outputs(ADC)
