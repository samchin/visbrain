"""Base class for objects of type brain."""
import os
import numpy as np
import logging

from vispy import scene

from .visbrain_obj import VisbrainObject
from ..visuals import BrainMesh
from ..utils import (get_data_path, mesh_edges, smoothing_matrix,
                     array2colormap)
from ..io import download_file, is_nibabel_installed, is_pandas_installed

logger = logging.getLogger('visbrain')


class BrainObj(VisbrainObject):
    """Create a brain object.

    Parameters
    ----------
    name : string
        Name of the brain object. If brain is 'B1' or 'B2' or 'B3' use a
        default brain template. If name is 'white', 'inflated' or
        'sphere' download the template (if needed). Otherwise, at least
        vertices and faces must be defined.
    vertices : array_like | None
        Mesh vertices to use for the brain. Must be an array of shape
        (n_vertices, 3).
    faces : array_like | None
        Mesh faces of shape (n_faces, 3).
    normals : array_like | None
        Normals to each vertex. If None, the program will try to compute it.
        Must be an array with the same shape as vertices.
    lr_index : array_like | None
        Left / Right index for hemispheres. Must be a vector of length
        n_vertices. This vector must be a boolean array where True refer to
        vertices that belong to the left hemisphere and False, the right
        hemisphere.
    hemisphere : {'left', 'both', 'right'}
        The hemisphere to plot.
    translucent : bool | True
        Use translucent (True) or opaque (False) brain.
    transform : VisPy.visuals.transforms | None
        VisPy transformation to set to the parent node.
    parent : VisPy.parent | None
        Brain object parent.
    verbose : string
        Verbosity level.

    Examples
    --------
    >>> from visbrain.objects import BrainObj
    >>> b = BrainObj('white', hemisphere='right', translucent=False)
    >>> b.preview(axis=True)
    """

    ###########################################################################
    ###########################################################################
    #                                BUILT IN
    ###########################################################################
    ###########################################################################

    def __init__(self, name, vertices=None, faces=None, normals=None,
                 lr_index=None, hemisphere='both', translucent=True,
                 transform=None, parent=None, verbose=None):
        """Init."""
        # Init Visbrain object base class :
        VisbrainObject.__init__(self, name, parent, transform, verbose)
        # Load brain template :
        self._scale = 1.
        self.set_data(name, vertices, faces, normals, lr_index, hemisphere)
        self.translucent = translucent
        self._data_color = []
        self._data_mask = []

    def __len__(self):
        """Get the number of vertices."""
        return self.vertices.shape[0]

    def set_data(self, name=None, vertices=None, faces=None, normals=None,
                 lr_index=None, hemisphere='both'):
        """Load a brain template."""
        # _______________________ DEFAULT _______________________
        b_download = self._get_downloadable_templates()
        b_installed = self._get_installed_templates()
        # Need to download the brain template :
        if (name in b_download) and (name not in b_installed):
            self._add_downloadable_templates(name)
        if name in self._get_installed_templates():  # predefined
            (vertices, faces, normals,
             lr_index) = self._load_brain_template(name)

        # _______________________ CHECKING _______________________
        assert all([isinstance(k, np.ndarray) for k in (vertices, faces)])
        if normals is not None:  # vertex normals
            assert isinstance(normals, np.ndarray)
        assert (lr_index is None) or isinstance(lr_index, np.ndarray)
        assert hemisphere in ['both', 'left', 'right']

        self._define_mesh(vertices, faces, normals, lr_index, hemisphere)

    def _define_mesh(self, vertices, faces, normals, lr_index, hemisphere):
        """Define brain mesh."""
        if not hasattr(self, 'mesh'):
            # Mesh brain :
            self.mesh = BrainMesh(vertices=vertices, faces=faces,
                                  normals=normals, lr_index=lr_index,
                                  hemisphere=hemisphere, parent=self._node,
                                  name='Mesh')
        else:
            self.mesh.set_data(vertices=vertices, faces=faces, normals=normals,
                               lr_index=lr_index, hemisphere=hemisphere)

    def _load_brain_template(self, name, path=None):
        """Load the brain template.

        If path is None, use the default visbrain/data folder.
        """
        if path is None:
            name = os.path.join(self._get_template_path(), name + '.npz')
        arch = np.load(name)
        vertices, faces = arch['vertices'], arch['faces']
        normals = arch['normals']
        lr_index = arch['lr_index'] if 'lr_index' in arch.keys() else None
        return vertices, faces, normals, lr_index

    ###########################################################################
    ###########################################################################
    #                           PATH METHODS
    ###########################################################################
    ###########################################################################

    def _get_template_path(self):
        """Get the path where datasets are stored."""
        return get_data_path(folder='templates')

    def _get_all_available_templates(self):
        """Get all available brain templates (e.g defaults and downloadable."""
        b_def = self._get_default_templates()
        b_down = self._get_downloadable_templates()
        b_installed = self._get_installed_templates()
        b_all = list(set(b_def + b_down + b_installed))
        b_all.sort()
        return b_all

    def _get_default_templates(self):
        """Get the default list of brain templates."""
        return ['B1', 'B2', 'B3']

    def _get_downloadable_templates(self):
        """Get the list of brain that can be downloaded."""
        logger.debug("hdr transformation missing for downloadable templates")
        return ['white', 'inflated', 'sphere']

    def _get_installed_templates(self):
        """Get the list of available brain templates."""
        all_files = os.listdir(self._get_template_path())
        surf_list = [os.path.splitext(k)[0] for k in all_files]
        surf_list.sort()
        return surf_list

    def _add_downloadable_templates(self, name):
        """Download then install a brain template."""
        assert name in self._get_downloadable_templates()
        to_path = self._get_template_path()
        # Download the file :
        download_file(name + '.npz', to_path=to_path)

    ###########################################################################
    ###########################################################################
    #                           CAMERA // ROTATION
    ###########################################################################
    ###########################################################################

    def _get_camera(self):
        """Get the most adapted camera."""
        if self.mesh._camera is None:
            camera = scene.cameras.TurntableCamera(name='turntable')
            self.mesh.set_camera(camera)
            self.reset_camera()
            self.rotate('top')
        return self.camera

    def _optimal_camera_properties(self, with_distance=True):
        """Get the optimal camera properties."""
        center = self.mesh._center * self._scale
        sc = 1.08 * self.mesh._camratio[-1]
        prop = {'center': center, 'scale_factor': sc, 'azimuth': 0.,
                'elevation': 90, 'distance': 4 * sc}
        if with_distance:
            return prop
        else:
            del prop['distance']
            return prop

    def reset_camera(self):
        """Reset the camera."""
        cam_args = self._optimal_camera_properties()
        self.mesh._camera.distance = cam_args['distance']
        del cam_args['distance']
        self.mesh._camera.set_state(cam_args)
        self.mesh._camera.set_default_state()

    def set_state(self, azimuth=None, elevation=None, scale_factor=None,
                  distance=None, center=None, margin=1.08):
        """Set the camera state."""
        distance = scale_factor * 4.
        if isinstance(azimuth, (int, float)):
            self.mesh._camera.azimuth = azimuth
        if isinstance(elevation, (int, float)):
            self.mesh._camera.elevation = elevation
        if isinstance(scale_factor, (int, float)):
            self.mesh._camera.scale_factor = margin * scale_factor * self.scale
        if isinstance(distance, (int, float)):
            self.mesh._camera.distance = distance * self.scale
        if (center is not None) and len(center) == 3:
            self.mesh._camera.center = center
        self.mesh._camera.update()

    def rotate(self, fixed='top', custom=None, margin=.08):
        """Rotate the brain using predefined rotations or a custom one.

        Parameters
        ----------
        fixed : str | 'top'
            Use a fixed rotation :

                * Top view : 'axial_0', 'top'
                * Bottom view : 'axial_1', 'bottom'
                * Left : 'sagittal_0', 'left'
                * Right : 'sagittal_1', 'right'
                * Front : 'coronal_0', 'front'
                * Back : 'coronal_1', 'back'
        custom : tuple | None
            Custom rotation. This parameter must be a tuple of two floats
            respectively describing the (azimuth, elevation).
        """
        # Create the camera if needed :
        self._get_camera()
        scale_factor = None
        if fixed in ['sagittal_0', 'left']:     # left
            azimuth, elevation = -90, 0
            scale_factor = self.mesh._camratio[-1]
        elif fixed in ['sagittal_1', 'right']:  # right
            azimuth, elevation = 90, 0
            scale_factor = self.mesh._camratio[-1]
        elif fixed in ['coronal_0', 'front']:   # front
            azimuth, elevation = 180, 0
            scale_factor = self.mesh._camratio[-1]
        elif fixed in ['coronal_1', 'back']:    # back
            azimuth, elevation = 0, 0
            scale_factor = self.mesh._camratio[-1]
        elif fixed in ['axial_0', 'top']:       # top
            azimuth, elevation = 0, 90
            scale_factor = self.mesh._camratio[1]
        elif fixed in ['axial_1', 'bottom']:    # bottom
            azimuth, elevation = 0, -90
            scale_factor = self.mesh._camratio[1]

        if isinstance(custom, (tuple, list)) and (len(custom) == 2):
            azimuth, elevation = tuple(custom)

        self.set_state(azimuth, elevation, scale_factor=scale_factor)

    def add_activation(self, data=None, vertices=None, smoothing_steps=20,
                       file=None, hemisphere=None, hide_under=None,
                       n_contours=None, cmap='viridis', clim=None, vmin=None,
                       vmax=None, under='gray', over='red'):
        """Add activation to the brain template.

        This method can be used for :

            * Add activations to specific vertices (`data` and `vertices`)
            * Add an overlay (`file` input)

        Parameters
        ----------
        data : array_like | None
            Vector array of data of shape (n_data,).
        vertices : array_like | None
            Vector array of vertices of shape (n_vtx). Must be an array of
            integers.
        smoothing_steps : int | 20
            Number of smoothing steps (smoothing is used if n_data < n_vtx)
        file : string | None
            Full path to the overlay file.
        hemisphrere : {None, 'both', 'left', 'right'}
            The hemisphere to use to add the overlay. If None, the method try
            to inferred the hemisphere from the file name.
        hide_under : float | None
            Hide activations under a certain threshold.
        n_contours : int | None
            Display activations as contour.
        cmap : string | 'viridis'
            The colormap to use.
        clim : tuple | None
            The colorbar limits. If None, (data.min(), data.max()) will be used
            instead.
        vmin : float | None
            Minimum threshold.
        vmax : float | None
            Maximum threshold.
        under : string/tuple/array_like | 'gray'
            The color to use for values under vmin.
        over : string/tuple/array_like | 'red'
            The color to use for values over vmax.
        """
        col_kw = dict(cmap=cmap, vmin=vmin, vmax=vmax, under=under, over=over,
                      clim=clim)
        is_under = isinstance(hide_under, (int, float))
        color = np.zeros((len(self.mesh), 4), dtype=np.float32)
        mask = np.zeros((len(self.mesh),), dtype=float)
        # ============================= METHOD =============================
        if isinstance(data, np.ndarray) and isinstance(vertices, np.ndarray):
            logger.info("Add data to secific vertices.")
            assert (data.ndim == 1) and (vertices.ndim == 1)
            assert isinstance(smoothing_steps, int)
            # Get smoothed vertices // data :
            edges = mesh_edges(self.mesh._faces)
            sm_mat = smoothing_matrix(vertices, edges, smoothing_steps)
            sm_data = data[sm_mat.col]
            # Clim :
            clim = (sm_data.min(), sm_data.max()) if clim is None else clim
            assert len(clim) == 2
            col_kw['clim'] = clim
            # Contours :
            sm_data = self._data_to_contour(sm_data, clim, n_contours)
            # Convert into colormap :
            smooth_map = array2colormap(sm_data, **col_kw)
            color = np.ones((len(self.mesh), 4), dtype=np.float32)
            color[sm_mat.row, :] = smooth_map
            # Mask :
            if is_under:
                mask[sm_mat.row[sm_data >= hide_under]] = 1.
            else:
                mask[:] = 0.
        elif isinstance(file, str):
            assert os.path.isfile(file)
            logger.info("Add overlay to the {} brain template "
                        "({})".format(self._name, file))
            assert is_nibabel_installed()
            import nibabel as nib
            # Load data using Nibabel :
            sc = nib.load(file).get_data().ravel(order="F")
            hemisphere = 'both' if len(sc) == len(self.mesh) else hemisphere
            # Hemisphere :
            hemisphere, idx = self._hemisphere_from_file(hemisphere, file)
            assert len(sc) == idx.sum()
            # Clim :
            clim = (sc.min(), sc.max()) if clim is None else clim
            assert len(clim) == 2
            col_kw['clim'] = clim
            # Contour :
            sc = self._data_to_contour(sc, clim, n_contours)
            # Convert into colormap :
            color[idx, :] = array2colormap(sc, **col_kw)
            # Mask :
            mask[idx] = 1.
            if is_under:
                sub_idx = np.where(idx)[0][sc < hide_under]
                mask[sub_idx] = 0.
        else:
            raise ValueError("Unknown activation type.")
        # Build mask color :
        col_mask = ~np.tile(mask.reshape(-1, 1).astype(bool), (1, 4))
        # Keep a copy of each overlay color and mask :
        self._data_color.append(np.ma.masked_array(color, mask=col_mask))
        self._data_mask.append(mask)
        # Set color and mask to the mesh :
        self.mesh.color = np.ma.array(self._data_color).mean(0)
        self.mesh.mask = np.array(self._data_mask).max(0)

    def parcellize(self, file, select=None, hemisphere=None, data=None,
                   cmap='viridis', clim=None, vmin=None, under='gray',
                   vmax=None, over='red'):
        """Parcellize the brain surface using a .annot file.

        This method require the nibabel package to be installed.

        Parameters
        ----------
        file : string
            Path to the .annot file.
        select : array_like | None
            Select the structures to display. Use either a list a index or a
            list of structure's names. If None, all structures are displayed.
        hemisphere : string | None
            The hemisphere for the parcellation. If None, the hemisphere will
            be inferred from file name.
        """
        idx, u_colors, labels, u_idx = self._load_annot_file(file)
        roi_labs = []
        # Get the hemisphere and (left // right) boolean index :
        hemisphere, h_idx = self._hemisphere_from_file(hemisphere, file)
        # Select conversion :
        if select is None:
            logger.info("Select all parcellates")
            select = u_idx
        # Manage color if data is an array :
        if isinstance(data, (np.ndarray, list, tuple)):
            data = np.asarray(data)
            assert data.ndim == 1 and len(data) == len(select)
            logger.info("Color inferred from data")
            u_colors = np.zeros((len(u_idx), 4), dtype=float)
            data_color = array2colormap(data, clim=clim, cmap=cmap, vmin=vmin,
                                        vmax=vmax, under=under, over=over)
        else:
            logger.info("Use default color included in the file")
            u_colors = u_colors.astype(float) / 255.
            data_color = None
        # Build the select variable :
        if isinstance(select, (np.ndarray, list)):
            select = np.asarray(select)
            if select.dtype != int:
                logger.info('Search parcellates using labels')
                select_str = select.copy()
                select = []
                for k in select_str:
                    label_idx = np.where(labels == k)[0]
                    if label_idx.size:
                        select.append(u_idx[label_idx])
                    else:
                        logger.warning("%r ignored. Use `get_parcellates` "
                                       "method to get the list of available "
                                       "parcellates" % k)
                        roi_labs.append('%s (ignored)' % k)
                select = np.array(select).ravel()
        if not select.size:
            raise ValueError("No parcellates found")
        # Prepare color variables :
        color = np.zeros((len(self.mesh), 4))
        mask = np.zeros((len(self.mesh),))
        # Set roi color to the mesh :
        sub_select = np.where(h_idx)[0]  # sub-hemisphere selection
        for i, k in enumerate(select):
            sub_idx = np.where(u_idx == k)[0]  # index location in u_idx
            if sub_idx:
                color_index = sub_select[u_idx[idx] == k]
                if data_color is None:
                    color[color_index, :] = u_colors[sub_idx, :]
                else:
                    color[color_index, :] = data_color[i, :]
                roi_labs.append(labels[sub_idx][0])
                mask[color_index] = 1.
            else:
                logger.error("An error occured for index %i" % k)
        logger.info("Selected parcellates : \n - %s" % "\n - ".join(roi_labs))
        # Keep an eye on data color and mask :
        self._data_color.append(color)
        self._data_mask.append(mask)
        # Set color and mask to the mesh :
        self.mesh.color = np.array(self._data_color).sum(0)
        self.mesh.mask = np.array(self._data_mask).sum(0)

    def get_parcellates(self, file):
        """Get the list of supported parcellates names and index.

        This method require the pandas and nibabel packages to be installed.

        Parameters
        ----------
        file : string
            Path to the .annot file.
        """
        assert is_pandas_installed()
        import pandas as pd
        idx, u_colors, labels, u_idx = self._load_annot_file(file)
        dico = dict(Index=u_idx, Labels=labels, Color=u_colors.tolist())
        return pd.DataFrame(dico, columns=['Index', 'Labels', 'Color'])

    @staticmethod
    def _data_to_contour(data, clim, n_contours):
        if isinstance(n_contours, int):
            _range = np.linspace(clim[0], clim[1], n_contours)
            for k in range(len(_range) - 1):
                d_idx = np.logical_and(data >= _range[k], data < _range[k + 1])
                data[d_idx] = _range[k]
        return data

    def _hemisphere_from_file(self, hemisphere, file):
        """Infer hemisphere from filename."""
        if hemisphere is None:
            _, filename = os.path.split(file)
            if any(k in filename for k in ['left', 'lh']):
                hemisphere = 'left'
            elif any(k in filename for k in ['right', 'rh']):
                hemisphere = 'right'
            else:
                hemisphere = 'both'
            logger.warning("%s hemisphere(s) inferred from "
                           "filename" % hemisphere)
        # Get index :
        if hemisphere == 'left':
            idx = self.mesh._lr_index
        elif hemisphere == 'right':
            idx = ~self.mesh._lr_index
        else:
            idx = np.ones((len(self.mesh),), dtype=bool)
        return hemisphere, idx

    @staticmethod
    def _load_annot_file(file):
        """Load a .annot file."""
        assert is_nibabel_installed()
        import nibabel
        # Get index and labels :
        assert os.path.isfile(file)
        idx, u_col, labels = nibabel.freesurfer.read_annot(file)
        idx, labels = np.array(idx).astype(int), np.array(labels).astype(str)
        logger.info("Annot file loaded (%s)" % file)
        return idx, u_col[:, 0:4], labels, u_col[..., -1]

    ###########################################################################
    ###########################################################################
    #                               PROPERTIES
    ###########################################################################
    ###########################################################################

    def __hemisphere_correction(self, arr, indexed_faces=False):
        mesh, hemi = self.mesh, self.mesh.hemisphere
        if hemi == 'both':
            return arr
        elif hemi in ['left', 'right']:
            lr = mesh._lr_index if hemi == 'left' else ~mesh._lr_index
            lr = mesh._lr_index[mesh._faces[:, 0]] if indexed_faces else lr
            return arr[lr, ...]

    # ----------- VERTICES -----------
    @property
    def vertices(self):
        """Get the vertices value."""
        return self.__hemisphere_correction(self.mesh._vertices)

    # ----------- FACES -----------
    @property
    def faces(self):
        """Get the faces value."""
        return self.__hemisphere_correction(self.mesh._faces, True)

    # ----------- NORMALS -----------
    @property
    def normals(self):
        """Get the normals value."""
        return self.__hemisphere_correction(self.mesh._normals)

    # ----------- HEMISPHERE -----------
    @property
    def hemisphere(self):
        """Get the hemisphere value."""
        return self.mesh.hemisphere

    @hemisphere.setter
    def hemisphere(self, value):
        """Set hemisphere value."""
        self.mesh.hemisphere = value

    # ----------- TRANSLUCENT -----------
    @property
    def translucent(self):
        """Get the translucent value."""
        return self.mesh.translucent

    @translucent.setter
    def translucent(self, value):
        """Set translucent value."""
        assert isinstance(value, bool)
        self.mesh.translucent = value

    # ----------- ALPHA -----------
    @property
    def alpha(self):
        """Get the alpha value."""
        return self.mesh.alpha

    @alpha.setter
    def alpha(self, value):
        """Set alpha value."""
        self.mesh.alpha = value

    # ----------- CAMERA -----------
    @property
    def camera(self):
        """Get the camera value."""
        return self.mesh._camera

    @camera.setter
    def camera(self, value):
        """Set camera value."""
        self.mesh.set_camera(value)
        self.reset_camera()

    # ----------- SCALE -----------
    @property
    def scale(self):
        """Get the scale value."""
        return self._scale

    @scale.setter
    def scale(self, value):
        """Set scale value."""
        self._scale = value
