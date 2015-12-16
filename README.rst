simple photo backup
===================

A very simple photo backup manager.

Installation
------------

If you want ot install SPB on your system:

.. code-block:: sh

    sudo python setup.py install
    spb --help

If you want to generate a single python file to put it on a USB drive for example:

.. code-block:: sh

    python setup.py unique_file -d /tmp/ -o my_spb
    cd /tmp
    ./my_spb --help


Usage
-----

You want to backup photo from `/media/camera` to `/media/usbdrive`

.. code-block:: sh

    ./my_spb -o /media/usbdrive /media/camera

I you want to configure the destination directories use the `-c` flag:

.. code-block:: sh

    ./my_spb -c -o /media/usbdrive /media/camera

