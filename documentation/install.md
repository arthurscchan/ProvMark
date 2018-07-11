# ProvMark Dependency

The major language used in ProvMark is Python3. So you need to ensure you have python3 installed.
Our tools basically support all unix-liked operating system.
As our tools aim to generate benchmark for different provenance collecting tools, we assumed that you have already install the provenance collecting tools and their repsective dependency properly before choosing that tools for the ProvMark system. The installation guide, dependencies and details documentations of the three currently supported tools can be found in the follow links.

- [SPADE](https://github.com/ashish-gehani/SPADE)
- [OPUS](https://www.cl.cam.ac.uk/research/dtg/fresco/opus/)
- [CamFlow](http://camflow.org/)

# ProvMark Installation

Install ProvMark is simple, just clone the whole git repository and you are good to go.

~~~~
git clone https://github.com/arthurscchan/ProvMark.git
~~~~

# Vagrant File


## Installation

In the vagrant folder, we also prepared the vagrant script for the three provenance collecting tools currently supported. If you have vagrant and virtual box installed in your system. You can follow the steps below to build up a virtual environment which everything (tools and ProvMark) are installed.

## SPADEv2 / SPADEv3

```
cd ./vagrant/spadev2 
# cd ./vagrant/spadev3
vagrant plugin install vagrant-vbguest
vagrant up
vagrant ssh
```

## OPUS

```
cd ./vagrant/spadev2
vagrant plugin install vagrant-vbguest
vagrant up
vagrant ssh
```

## CamFlow

```
cd ./vagrant/camflow
vagrant plugin install vagrant-vbguest
vagrant up
vagrant halt
vagrant up
vagrant ssh
```

After the above steps, you should be given a ssh connection connects to the virtual machine which you can start ProvMark on your chosen tools directly.
Note: the installation process can take an extended amount of time depending on your configuration.

