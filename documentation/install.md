# ProvMark Dependency

The major language used in ProvMark is Python3. So you need to ensure you have python3 installed.
Our tools basically support all unix-liked operating system.
As our tools aim to generate benchmark for different provenance collecting tools, we assumed that you have already install the provenance collecting tools and their repsective dependency properly before choosing that tools for the ProvMark system. The installation guide, dependencies and details documentations of the three currently supported tools can be found in the follow links.

- [SPADE](https://github.com/ashish-gehani/SPADE)
- [OPUS](https://www.cl.cam.ac.uk/research/dtg/fresco/opus/)
- [CamFlow](http://camflow.org/)

# ProvMark Installation

Install ProvMark is simple, just clone the whole git repository and you are good to go. The current stable version is tagged by tag Middleware2019.

~~~~
git clone https://github.com/arthurscchan/ProvMark.git
cd ProvMark
git checkout Middleware2019
~~~~

# Vagrant File


## Installation

In the vagrant folder, we also prepared the vagrant script for the three provenance collecting tools currently supported. If you have vagrant and virtual box installed in your system. You can follow the steps below to build up a virtual environment which everything (tools and ProvMark) are installed.

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
# cd ./vagrant/camflowv043
vagrant plugin install vagrant-vbguest
vagrant up
vagrant halt
vagrant up
vagrant ssh
```
It is necessary to reboot so that the camflow-enabled kernel will be used.  This kernel should be highlighted as the first entry by the boot loader but if not, it should be selected.


After the above steps, you should be given a ssh connection connects to the virtual machine which you can start ProvMark on your chosen tools directly.
Note: the installation process can take an extended amount of time depending on your configuration.

