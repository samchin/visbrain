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
Sleep(data='test_files/sleep-900.edf', config_file = "test_files/sleep-900_config.json", hypno="test_files/sleep-900_hypno.txt").show()




# Sleep(data='test_files/1.rec', config_file="test_files/config_1.json").show()




