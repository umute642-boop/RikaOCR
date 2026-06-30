# SPDX-License-Identifier: Apache-2.0
"""Dataset layer: line cropping, splitting, manifests, and dataset building.

Image-handling submodules (``image_io``, ``cropping``) require the optional
``[data]`` extra (Pillow, NumPy). Import them explicitly; this package's
``__init__`` deliberately does not, so pure-stdlib helpers like ``splitting``
remain usable without the image stack installed.
"""
