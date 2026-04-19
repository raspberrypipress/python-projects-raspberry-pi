#include <Python.h>

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#include "piolib.h"
#include "uart_tx.pio.h"
#include "uart_rx.pio.h"

static PyObject* load_uart_tx_sm(PyObject *self, PyObject *args) {

    int sm;
    uint offset;
    uint gpio;
    uint baud;
    PIO pio;
    if (!PyArg_ParseTuple(args, "ii", &gpio, &baud)) 
        return NULL;    

    pio = pio0;
    sm = pio_claim_unused_sm(pio, true);
    pio_sm_config_xfer(pio, sm, PIO_DIR_TO_SM, 256, 1);
    offset = pio_add_program(pio, &uart_tx_program);
    pio_sm_clear_fifos(pio, sm);
  
    uart_tx_program_init(pio, sm, offset, gpio, baud);
    return PyLong_FromLong(sm);
}

static PyObject* load_uart_rx_sm(PyObject *self, PyObject *args) {
    int sm;
    uint offset;
    uint gpio;
    uint baud;
    PIO pio;
    
    if (!PyArg_ParseTuple(args, "ii", &gpio, &baud)) 
        return NULL;    
    pio = pio0;
    sm = pio_claim_unused_sm(pio, true);
    pio_sm_config_xfer(pio, sm, PIO_DIR_TO_SM, 256, 1);
   
    offset = pio_add_program(pio, &uart_rx_program);
    pio_sm_clear_fifos(pio, sm);
    uart_rx_program_init(pio, sm, offset, gpio, baud);
    return PyLong_FromLong(sm);
}

static PyObject* get_uart_data(PyObject *self, PyObject *args) {
    PIO pio;
    int sm;
    int n;
    int ret;
    int size;
    pio = pio0;

    if (!PyArg_ParseTuple(args, "i", &sm)) 
        return NULL;

    size = pio_sm_get_rx_fifo_level(pio, sm);
    
    char data[size+1];
    
    for (int i=0; i<size; i++) {
        ret = pio_sm_get_blocking(pio, sm);
        data[i] = (char)(ret>>24);
    }
    data[size] = '\0';
    return Py_BuildValue("s", data);
}

// NOTE -- C strings for uart are 8 bit chars. This doesn't map to Python
// looks like it actually puts characters as a uint32_c
static PyObject* send_uart_data(PyObject *self, PyObject *args) {
    PIO pio;
    int sm;
    Py_buffer data;
    pio = pio0;

    if (!PyArg_ParseTuple(args, "iy*", &sm, &data)) 
        return NULL;
    uint32_t *data_array = (uint32_t *)data.buf;
    uart_tx_program_puts(pio, sm, (char*) data_array);

    PyBuffer_Release(&data);
    Py_RETURN_NONE;
}

// Exported methods are collected in a table
PyMethodDef method_table[] = {
    {"load_uart_tx_sm", (PyCFunction) load_uart_tx_sm, METH_VARARGS, "Method docstring"},
    {"load_uart_rx_sm", (PyCFunction) load_uart_rx_sm, METH_VARARGS, "Method docstring"},
    {"send_uart_data", (PyCFunction) send_uart_data, METH_VARARGS, "Method docstring"},
    {"get_uart_data", (PyCFunction) get_uart_data, METH_VARARGS, "Method docstring"},
    {NULL, NULL, 0, NULL} // Sentinel value ending the table
};

// A struct contains the definition of a module
PyModuleDef uart_pio_module = {
    PyModuleDef_HEAD_INIT,
    "mymodule", // Module name
    "This is the module docstring",
    10000,   // Optional size of the module state memory
    method_table,
    NULL, // Optional slot definitions
    NULL, // Optional traversal function
    NULL, // Optional clear function
    NULL  // Optional module deallocation function
};

// The module init function
PyMODINIT_FUNC PyInit_uart_pio(void) {
    return PyModule_Create(&uart_pio_module);
}
