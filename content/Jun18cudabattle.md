Title: Getting CUDA working on a laptop with two GPUs
Date: 2016-01-18
Category: cuda
Tags: cuda, neural networks

I had a lot of trouble setting up my laptop NVIDIA GPU with CUDA on Ubuntu
14.04. These steps might actually help somebody.

First, download the [NVIDIA CUDA Toolkit](http://developer.nvidia.com/cuda-downloads).

Remove all old NVIDIA-related drivers:

    :::bash
    sudo apt-get remove --purge nvidia*
    sudo apt-get --purge remove xserver-xorg-video-nouveau

Backup your `/etc/modprobe.d/blacklist.conf` and make sure it contains these lines:

    :::bash
    blacklist nouveau
    blacklist lbm-nouveau
    blacklist nvidia-173
    blacklist nvidia-96
    blacklist nvidia-current
    blacklist nvidia-173-updates
    blacklist nvidia-96-updates
    alias nvidia nvidia_current_updates
    alias nouveau off
    alias lbm-nouveau off
    options nouveau modeset=0

Add bumblebee and xorg-edgers repositories:

    :::bash
    sudo apt-add-repository ppa:bumblebee/stable -y
    sudo add-apt-repository ppa:xorg-edgers/ppa -y
    sudo apt-get update && sudo apt-get upgrade -y

Now it's time to install the CUDA toolkit (along with `nvidia-352` drivers).

    :::bash
    # This installs necessary headers.
    sudo apt-get install linux-source && sudo apt-get install linux-headers-$(uname -r)

    # USE THE REAL PACKAGE NAME BELOW
    sudo dpkg -i cuda-repo-ubuntu1404-7-5-local_7.5-18_amd64.deb

    sudo apt-get install cuda
    sudo apt-get update
    sudo apt-get dist-upgrade -y

Install bumblebee (to have switchable GPUs).

    :::bash
    sudo apt-get install bumblebee bumblebee-nvidia virtualgl virtualgl-libs virtualgl-libs-ia32:i386 virtualgl-libs:i386
    sudo usermod -a -G bumblebee $USER

Edit `/etc/bumblebee/bumblebee.conf` as follows:

* Change all occurences of `nvidia-current` to `nvidia-352`
* After `Driver=` insert `nvidia`
* After `KernelDriver=` insert `nvidia-352`
* (if having trouble with optirun) uncomment the `BusID` line and set it
  accordingly to what the comment above this line says.

Make sure that these lines are in `/etc/modprobe.d/bumblebee.conf`:

    :::bash
    blacklist nvidia-352
    blacklist nvidia-352-updates
    blacklist nvidia-experimental-352

    alias nvidia-uvm nvidia_352_uvm


After `reboot` everything should work fine. You can test it with:

    :::bash
    optirun glxspheres64
    # compare the performance with default GPU running the command above without optirun

If you need more help: [CUDA installation guide for Linux](http://developer.download.nvidia.com/compute/cuda/7.5/Prod/docs/sidebar/CUDA_Installation_Guide_Linux.pdf)
