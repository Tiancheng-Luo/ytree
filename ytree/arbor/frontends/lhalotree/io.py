"""
LHaloTreeArbor io classes and member functions



"""

#-----------------------------------------------------------------------------
# Copyright (c) 2017, Britton Smith <brittonsmith@gmail.com>
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------

import numpy as np

from ytree.arbor.io import \
    TreeFieldIO

class LHaloTreeTreeFieldIO(TreeFieldIO):

    def _read_fields(self, root_node, fields, dtypes=None,
                     f=None, root_only=False):
        """
        Read fields from disk for a single tree.

        Here we accept a list of fields and return a dictionary of NumPy
        arrays for each field.

        dtypes will be an optional dictionary of type for each field

        f will optionally be the already-opened file handle.

        If root_only is true, we only want the field value for the root
        of the tree.

        Below is the example for ctrees.
        """
        if dtypes is None:
            dtypes = {}

        # Don't read all data if only uid/desc_uid requested
        lht = root_node._lht
        data = None
        for field in fields:
            if field not in ['uid', 'desc_uid']:
                if root_only:
                    data = lht.read_single_halo(root_node._index_in_lht, 0, fd=f)
                else:
                    data = lht.read_single_lhalotree(root_node._index_in_lht, fd=f)
                break
        if data is None:
            data = dict()
            if root_only:
                halonum = 0
            else:
                halonum = None
            data['uid'] = lht.get_halo_uid(
                root_node._index_in_lht, halonum)
            data['desc_uid'] = lht.get_halo_desc_uid(
                root_node._index_in_lht, halonum)

        if isinstance(data, np.ndarray):
            # nhalos = len(data)
            field_data = {}
            for field in fields:
                # Copy makes array contiguous in memory, but also uses more memory
                dtype = dtypes.get(field, float)
                field_data[field] = data[field].astype(dtype)
                # field_data[field] = np.zeros(nhalos, dtype=dtype)
                # field_data[field][:] = data[field]
        else:
            assert(isinstance(data, dict))
            # TODO: Is there a reason for a specific data type other than
            # native? If so, the fields need converted here
            # field_data = {}
            # for field in fields:
            #     dtype = dtypes.get(field, float)
            #     field_data[field] = data[field].astype(dtype)
            field_data = data

        # apply field units
        fi = self.arbor.field_info
        for field in fields:
            units = fi[field].get("units", "")
            if units != "":
                field_data[field] = \
                  self.arbor.arr(field_data[field], units)

        return field_data
