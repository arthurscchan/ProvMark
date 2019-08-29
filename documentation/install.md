# ProvMark Dependency

The major language used in ProvMark is Python3. So you need to ensure you have python3 installed.
Our tools basically support all unix-like operating system.
As our tools aim to generate benchmarks for different provenance collecting systems, we assume that you have already install the provenance collecting tools and their repsective dependency properly before choosing that tools for the ProvMark system. The installation guide, dependencies and details documentations of the three currently supported tools can be found in the following links.

- [SPADE](https://github.com/ashish-gehani/SPADE)
- [OPUS](https://www.cl.cam.ac.uk/research/dtg/fresco/opus/)
- [CamFlow](http://camflow.org/)

You may also use our provided [Vagrant](https://www.vagrantup.com/) script to automatically build a virtual environment and install all dependencies (including the provenance system chosen) for ProvMark. You may also need to install [Virtual Box](https://www.virtualbox.org/) for using the built virtual machine.

# ProvMark Installation

Installing ProvMark is simple, just clone the whole git repository.

~~~~
git clone https://github.com/arthurscchan/ProvMark.git
~~~~

# Vagrant File


## Installation

In the vagrant folder, we have prepared the [Vagrant](https://www.vagrantup.com/) script for the three provenance collecting tools currently supported. If you have vagrant and virtual box installed in your system, you can follow the steps below to build up a virtual environment which everything (tools and ProvMark) are installed.

## SPADEv3

``` shell
cd ./vagrant/spadev3
vagrant plugin install vagrant-vbguest
vagrant up
vagrant ssh
```

## OPUS

``` shell
cd ./vagrant/opus
vagrant plugin install vagrant-vbguest
vagrant up
vagrant ssh
```

To run OPUS, you also need a source or binary distribution for hte OPUS system itself, which is not currently available online.  Please contact the authors (http://www.cl.cam.ac.uk/research/dtg/fresco/opus/).

## CamFlow

``` shell
cd ./vagrant/camflowv045
vagrant plugin install vagrant-vbguest
vagrant up
vagrant halt
vagrant up
vagrant ssh
```
It is necessary to reboot the VM (halt / up) so that the camflow-enabled kernel will be used.  This kernel should be highlighted as the first entry by the boot loader but if not, it should be selected.


After the above steps, you should be given a ssh connection connected to the virtual machine which you can start ProvMark on your chosen tools directly.
Note: the installation process can take an extended amount of time depending on your configuration.

