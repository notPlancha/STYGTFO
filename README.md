# stygtfo
A simple tool to comment out packages not used in a latex document.

Why? Because I usually experiment with packages a lot and in the end I don't use them all, but it's basically impossible to know which ones I don't use.

This pacakge compiles the document with every package commented out one by one, and compares the expected pdf output with the actual pdf output. If the pdf output is the same, the package is determined not used and commented out.

This package is not tested basically at all, and I only used tectonic to test it (beacuse the others are slow and don't garantee the packages are installed). It might not work with other engines. In fact, it probably won't. Maybe in the future I'll update it, but I doubt it. Fell free to fork it and make PRs.

## Usage
```bash
stygtfo <pathToTexFile> [--output <outputfile>] [--engine <pathToEngine>] [--verbose <bool>] [--args <argsToPassToEngine>] [--temp <pathToTempDir>]
```
Currently, the `--args` option is not implemented, if some interest is shown I'm free to do it.


```python
import stygtfo
stygtfo.CheckUnusedPackages("path/to/file.tex", "path/to/engin", usedPackages=None, resultedPath=None, verbose=False, pathToTemp=None)
```

## Installation
```bash
pip install --user stygtfo
```
You will need the same requirements as [diff-pdf-visually](https://github.com/bgeron/diff-pdf-visually#how-to-install-this), which on Windows is ImageMagick and Poppler. You can get them on chocolatey too.

I don't know if the `--user` flag is actually needed, but I had some problems with it, so I recommend using it (except if you're installing it in a virtualenv).

You can also run it directly with, for example, `uv`.
```bash
uvx stygtfo # or uv tool run stygtfo
```