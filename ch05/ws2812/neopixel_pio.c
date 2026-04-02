#include <Python.h>

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#include "piolib.h"
#include "ws2812.pio.h"

__thread char prevent_segfault;


static PyObject* load_neopixel_sm(PyObject *self, PyObject *args) {

    int sm;
    uint offset;
    uint gpio;
    PIO pio;
    
    if (!PyArg_ParseTuple(args, "i", &gpio)) 
        return NULL;
    
    pio = pio0;
    sm = pio_claim_unused_sm(pio, true);
    pio_sm_config_xfer(pio, sm, PIO_DIR_TO_SM, 256, 1);
    offset = pio_add_program(pio, &ws2812_program);  
    ws2812_program_init(pio, sm, offset, gpio, 800000.0, false);
    return PyLong_FromLong(sm);

}

static PyObject* send_neopixel_data(PyObject *self, PyObject *args) {
    PIO pio;
    int sm;
    int red;
    int green;
    int blue;
    Py_buffer data;

    pio = pio0;

    if (!PyArg_ParseTuple(args, "iy*", &sm, &data)) 
        return NULL;
        
    int *data_array = (int *)data.buf;
    
    pio_sm_config_xfer(pio, sm, PIO_DIR_TO_SM, 256, 1);
    pio_sm_xfer_data(pio, sm, PIO_DIR_TO_SM, data.len, data_array);

Py_RETURN_NONE;

}


// Exported methods are collected in a table
PyMethodDef method_table[] = {
    {"load_neopixel_sm", (PyCFunction) load_neopixel_sm, METH_VARARGS, "Load the WS2812 PIO program using the pin number passed as an argument and return the state machine number"},
    {"send_neopixel_data", (PyCFunction) send_neopixel_data, METH_VARARGS, "Takes an statemachine number and an array and sends the data to the statemachine"},
    {NULL, NULL, 0, NULL} // Sentinel value ending the table
};

// A struct contains the definition of a module
PyModuleDef neopixel_pio_module = {
    PyModuleDef_HEAD_INIT,
    "mymodule", // Module name
    "A WS2812 driver for use with the neopixel_rpi5 module",
    10000,   // Optional size of the module state memory
    method_table,
    NULL, // Optional slot definitions
    NULL, // Optional traversal function
    NULL, // Optional clear function
    NULL  // Optional module deallocation function
};

// The module init function
PyMODINIT_FUNC PyInit_neopixel_pio(void) {
    return PyModule_Create(&neopixel_pio_module);
}
