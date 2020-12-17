
Skull Base Navigation
=====================

.. image:: https://github.com/UCL/SkullBaseNavigation/raw/master/project-icon.png
   :height: 128px
   :width: 128px
   :target: https://github.com/UCL/SkullBaseNavigation


Author: Thomas Dowrick

Skull Base Navigation was developed at the `Wellcome EPSRC Centre for Interventional and Surgical Sciences`_ in `University College London (UCL)`_.


Requirements
^^^^^^^^^^^^

See the `wiki
<https://github.com/UCL/SkullBaseNavigation/wikis/home>`_.

Guide
^^^^^

- Check that BK5000, laptop and StealthStation are connnected to the network switch.
- Power on all devices (BK, laptop, Stealth, network switch).
- The first server to be started up is the one that allows the connection to the BK5000 (pyIGTLink server). This is done by double-clicking on the `launch_bk` icon.
- The second server to be started up (PLUS server) is the one that allows the synchronous connection and collection of data between the BK5000 (ultrasound images) and the StealthStation (tracking and positioning data). This is done by double-clicking on the `launch_plus` icon.
- Finally, the slicelet is to be started up. This is done by simply double-clicking on the `launch_slicelet` icon.
- If everything runs well, the final steps to be executed within the slicelet are:
  - Pull the US images from the BK500 by clicking on the `Connect to OpenIGTLink` button.
  - Pull the CT model from the StealthStation by clicking on the `Get Model From Remote` button.
  - After a short time, you will be able to visualise both the stream of US images and the CT model in the 3D view. Then, you are ready to perform the pivot and spin calibrations by clicking on the `Pivot Calibration` button.

From this point on, the start up is finished. You should be able to visualise in real-time the stream of US images together with the CT scan and ready to perform the live reconstruction.

NB. The following is for a direct start up of the slicelet. This is mostly intended for development purposes. The below assumes that you are in the root directory of the **SkullBaseNavigation** repository.

Run the slicelet:
::
    /path/to/slicer/Slicer --no-main-window --python-script skullbasenavigation/sbn_slicelet.py
    
*no_main_window* runs the slicelet standalone, running without this also launches the standard Slicer GUI.

There are some basic unit tests implemented, these can be ran using:

::

    /path/to/slicer/Slicer --python-script skullbasenavigation/testing_slicer_functions.py

    


Contributing
^^^^^^^^^^^^

Please see the `contributing guidelines`_.


Licensing and copyright
-----------------------

Copyright 2021 University College London.
Skull Base Navigation is released under the BSD-3 license. Please see the `license file`_ for details.


Acknowledgements
----------------

Supported by `Wellcome`_ and `EPSRC`_.


.. _`Wellcome EPSRC Centre for Interventional and Surgical Sciences`: http://www.ucl.ac.uk/weiss
.. _`source code repository`: https://github.com/UCL/SkullBaseNavigation
.. _`Documentation`: https://SkullBaseNavigation.readthedocs.io
.. _`University College London (UCL)`: http://www.ucl.ac.uk/
.. _`Wellcome`: https://wellcome.ac.uk/
.. _`EPSRC`: https://www.epsrc.ac.uk/
.. _`contributing guidelines`: https://github.com/UCL/SkullBaseNavigation/blob/master/CONTRIBUTING.rst
.. _`license file`: https://github.com/UCL/SkullBaseNavigation/blob/master/LICENSE
