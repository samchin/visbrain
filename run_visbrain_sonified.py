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
import numpy as np

###############################################################################
#                               LOAD YOUR FILE
#############################################################################


# Open the GUI :
# Sleep(data='test_files/sleep-900.edf', config_file = "test_files/sleep-900_config.json", hypno="test_files/sleep-900_hypno.txt").show()

# NUM_SAMPLES = 6

# FILE_PATHS = ['normal_sleep_data/1.rec', 'normal_sleep_data/2.rec',  'normal_sleep_data/3.rec',  'normal_sleep_data/4.rec',  'normal_sleep_data/5.rec',   
# 'normal_sleep_data/6.rec',  'normal_sleep_data/7.rec',  'normal_sleep_data/8.rec',  'normal_sleep_data/9.rec',  'normal_sleep_data/10.rec']  
# FILE_MAX_TIME= [28590.0, 28200.0, 24690.0, 23790.0, 28290.0, 25560.0, 24390.0, 29970.0, 29040.0, 23850.0]
# NUM_FILES = len(FILE_PATHS)

# def random_divisible_by_30(N):
#     max_num = (N // 30) * 30
#     num = np.random.randint(1, max_num + 1)
#     num = num - (num % 30)
#     return num

# for _ in range(NUM_SAMPLES):
#     # select a file to sample from
#     selection = np.random.choice(np.arange(NUM_FILES))
#     sleep_file = FILE_PATHS[selection]
#     # sample a random time that is divisible by 30 from that file
#     epoch = random_divisible_by_30(FILE_MAX_TIME[selection])
#     print(sleep_file, epoch)

Sleep(data='normal_sleep_data/1.rec', config_file="normal_sleep_data/config.json").show()









