# Introduction

This package contains OpenSCAD-style CAD software based around OpenCASCADE.

Please be patient: **bcad** will probably never support 100% of OpenSCAD features; I hope to make **bcad** more capable one day, retaining support for OpenSCAD way of doing things to some degree though.

# Installation

## Debian

Bcad requires **ezdxf** python module, which can be installed from here: https://github.com/snegovick/ezdxf (read the README).

Most of the other dependencies are either available in **debian** itself or contained inside the package.

Download pre-built packages from [releases page](https://github.com/snegovick/bcad/releases).

# How to use

To use bcad open up your terminal, and try to open your **.scad** file like this:

```
bcad-launcher --file <your_file.scad>
```

Saving is done via commandline like this:

```
bcad-launcher --file <your_file.scad> --output <your_output.step>
```

STEP, STL and DXF output formats are supported.

DXF support is in early stages of development.
