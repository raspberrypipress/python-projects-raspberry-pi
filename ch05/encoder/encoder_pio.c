#include <Python.h>

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#include "piolib.h"
#include "quadrature_encoder.pio.h"

__thread char prevent_segfault;

static PyObject* load_encoder_sm(PyObject *self, PyObject *args) {

    int sm;
    uint offset;
    uint gpio;
    PIO pio;
    
    if (!PyArg_ParseTuple(args, "i", &gpio)) 
        return NULL;    
        
    pio = pio0;
    sm = pio_claim_unused_sm(pio, true);

    pio_sm_config_xfer(pio, sm, PIO_DIR_TO_SM, 256, 1);
    
    pio_clear_instruction_memory(pio); // a bit risky? This will do it for everything and could break other hardware running even if we don't want it? leave for now.
    offset = pio_add_program(pio, &quadrature_encoder_program);

    pio_sm_clear_fifos(pio, sm);
    
    quadrature_encoder_program_init(pio,sm,gpio,0);
    return PyLong_FromLong(sm);

}

static PyObject* get_encoder_data(PyObject *self, PyObject *args) {
    PIO pio;
    int sm;
    int n;
    int ret;
    int size;

    pio = pio0;

    if (!PyArg_ParseTuple(args, "i", &sm)) 
        return NULL;
    

    return PyLong_FromLong(quadrature_encoder_get_count(pio,sm));
}

// Exported methods are collected in a table
PyMethodDef method_table[] = {
    {"load_encoder_sm", (PyCFunction) load_encoder_sm, METH_VARARGS, "Method docstring"},
    {"get_encoder_data", (PyCFunction) get_encoder_data, METH_VARARGS, "Method docstring"},
    {NULL, NULL, 0, NULL} // Sentinel value ending the table
};

// A struct contains the definition of a module
PyModuleDef encoder_pio_module = {
    PyModuleDef_HEAD_INIT,
    "encoder_pio", // Module name
    "This is the module docstring",
    10000,   // Optional size of the module state memory
    method_table,
    NULL, // Optional slot definitions
    NULL, // Optional traversal function
    NULL, // Optional clear function
    NULL  // Optional module deallocation function
};

// The module init function
PyMODINIT_FUNC PyInit_encoder_pio(void) {
    return PyModule_Create(&encoder_pio_module);
}

