"""
Cross-section object
====================

Illustration and main functionalities and inputs of the cross-section object.

.. image:: ../../picture/picobjects/ex_cs_obj.png
"""
from visbrain.objects import CrossSecObj, SceneObj
from visbrain.io import download_file

sc = SceneObj()
CS_KW = dict(text_size=8.)

# print("""
# # =============================================================================
# #                              Brodmann area
# # =============================================================================
# """)
# cs_brod = CrossSecObj('brodmann', **CS_KW)
# cs_brod.localize_source((-10., -15., 20.))
# sc.add_to_subplot(cs_brod, row=0, col=0)

# print("""
# # =============================================================================
# #                              Nii.gz file
# # =============================================================================
# """)
# path = download_file('GG-853-GM-0.7mm.nii.gz', astype='example_data')
path = "/home/etienne/anaconda3/envs/pyqt5/lib/python3.6/site-packages/nilearn/datasets/data/avg152T1_brain.nii.gz"
cs_cust = CrossSecObj(path, coords=(0., 0., 0.), **CS_KW)
f = "/home/etienne/nilearn_data/brainomics_localizer/brainomics_data/S02/t_map_left_auditory_&_visual_click_vs_right_auditory&visual_click.nii.gz"
cs_cust.set_activation(f, translucent=(-2.9, 2.9), cmap='bwr')
cs_cust.localize_source((39, -19, 55))
cs_cust.preview()
0/0
sc.add_to_subplot(cs_cust, row=0, col=1)

sc.preview()
