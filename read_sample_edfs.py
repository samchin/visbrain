"""
Load EDF file
=============

This example demonstrate how to load an EDF file.

Required dataset at :
https://www.dropbox.com/s/bj1ra95rbksukro/sleep_edf.zip?dl=1

.. image:: ../../_static/examples/ex_LoadEDF.png
"""
import os


from visbrain.gui import Sleep

###############################################################################
#                               LOAD YOUR FILE
#############################################################################


# Open the GUI :
# Sleep(data='sleep-900.edf', config_file = "config.json", hypno="sleep-900_hypno.txt").show()


Sleep(data='1.rec', config_file="config_1.json").show()




