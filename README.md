[![Build Status](https://travis-ci.org/johnnyiller/cluster_funk.svg?branch=master)](https://travis-ci.org/johnnyiller/cluster_funk)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=johnnyiller_cluster_funk&metric=bugs)](https://sonarcloud.io/dashboard?id=johnnyiller_cluster_funk)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=johnnyiller_cluster_funk&metric=code_smells)](https://sonarcloud.io/dashboard?id=johnnyiller_cluster_funk)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=johnnyiller_cluster_funk&metric=coverage)](https://sonarcloud.io/dashboard?id=johnnyiller_cluster_funk)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=johnnyiller_cluster_funk&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=johnnyiller_cluster_funk)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=johnnyiller_cluster_funk&metric=security_rating)](https://sonarcloud.io/dashboard?id=johnnyiller_cluster_funk)
[![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=johnnyiller_cluster_funk&metric=sqale_index)](https://sonarcloud.io/dashboard?id=johnnyiller_cluster_funk)

# cluster_funk
*An opinionated framework for running big data jobs*

For usage please [click here](http://www.jefferydurand.com/cluster_funk)

If you'd like to work on this tool please read the rest of this readme to get set up with a development environment.

# Contribute

## Installation


```
$ pip install -r requirements.txt

$ pip install setup.py
```

## Development

This project includes a number of helpers in the `Makefile` to streamline common development tasks.

### Environment Setup

The following demonstrates setting up and working with a development environment:

```
### create a virtualenv for development

$ make virtualenv

$ source env/bin/activate


### run cluster_funk cli application

$ cluster_funk --help


### run pytest / coverage

$ make test
```

