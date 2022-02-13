# kuma-zerolb
Playground to test the [Zero LB  concept](https://konghq.com/blog/zerolb/) with Kuma

# Overview

# Requirements

This is a Python 3 program that automates several other tools.

Make sure you have Python 3 installed:

```
$ brew install python
```  

Install `pyenv`:

```
brew install pyenv
```

Install `poetry`:

```
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -
```

Set up a virtual environment for the project:

```
pyenv install 3.9.6
pyenv local 3.9.6
poetry install 
```


# Usage

You must bring your own clusters. 
This program requires 3 different clusters to serve as
a management cluster and two remote clusters.

## Prepare the configuration
Copy the `sample_config.py` file into a file called `config.py` and 
update the kube_contexts dictionary to point to the kube contexts 
(from your ./kube/config file).

Then run:

```
poetry run python kuma_zerolb.py
```

This will deploy Kuma in a multi-zone configuration into your
clusters.

# Reference

