import subprocess
import hashlib
import argparse
import os
import shutil
import tempfile
from pathlib import Path
from diff_pdf_visually import pdf_similar, pdftopng


def main():
    # region Argument parsing building
    parser = argparse.ArgumentParser(description='STYGTFO')
    parser.add_argument('-o', '--output', type=str, help='output file, if none provided it will replace the input path',
                        default="")
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose output', default=False)
    parser.add_argument('-e', "--engine", type=str,
                        help='Command \\ Path to engine, defaults to (and only tested with) tectonic',
                        default="tectonic")
    parser.add_argument('-a', "--args", type=str, help='Arguments to engine', default="")
    parser.add_argument('-t', "--temp", type=str, help='Path to temporary directory', default="")
    parser.add_argument('path', metavar='path', type=str, nargs='+', help='path to latex file')
    # endregion
    # region Argument parsing
    args = parser.parse_args()
    if len(args.path) != 1:
        parser.print_help()
        exit(1)
    if args.verbose: print("Checking engine")
    engine = shutil.which(args.engine)
    if engine is None:
        print("Engine not found")
        exit(1)
    if args.verbose: print("Engine found at: " + engine)

    if args.verbose: print("Checking input file")
    if not os.path.isfile(args.path[0]):
        print("Input file not found")
        exit(1)
    inputFile = os.path.abspath(args.path[0])
    if args.verbose: print("Input file found at: " + inputFile)
    output = inputFile if args.output == "" else args.output

    if args.verbose: print("Will output to " + output)

    if args.verbose: print("Getting packages used")
    packages = getUsedPackages(inputFile)
    if len(packages) == 0:
        print("No packages found in file " + inputFile)
        exit(0)
    if args.verbose: print("Packages found at lines " + str(packages))

    if args.verbose: print("Checking temporary directory")
    tempdir = tempfile.gettempdir() if args.temp == "" else args.temp
    if args.verbose: print("Temporary directory at: " + tempdir)

    unused = CheckUnusedPackages(inputFile, engine, packages, verbose=args.verbose, pathToTemp=tempdir)
    if args.verbose: print("Unused packages found at lines " + str(unused))
    if args.verbose: print("Removing unused packages")
    with open(inputFile, 'r', encoding="utf-8") as f:
        lines = f.readlines()
    with open(output, 'w', encoding="utf-8") as f:
        for line in unused:
            lines[line] = "%" + lines[line]
        f.write("".join(lines))
    if args.verbose: print("Unused packages removed")
    exit(0)

def compileFile(filePath, pathToTemp=None, pathToEngine=None, verbose=False) -> str | None:
    if pathToTemp is None: pathToTemp = tempfile.gettempdir()
    if pathToEngine is None: raise ValueError("pathToEngine is required")
    Path(pathToTemp).mkdir(parents=True, exist_ok=True)
    pathToTemp = pathToTemp.replace("\\", "/")
    completedProcess = subprocess.run([pathToEngine, filePath, "-o", pathToTemp], capture_output=True)
    if completedProcess.returncode != 0:
        return None
    # change filePath to the compiled file
    CompiledFilePath = os.path.join(pathToTemp, os.path.basename(filePath).split(".")[0] + ".pdf")
    return CompiledFilePath


def getUsedPackages(filePath, verbose=False) -> list[int]:
    # TODO make verbose
    with open(filePath, 'r', encoding="utf-8") as f:
        lines = f.readlines()
    ret = []
    for line, lineContent in enumerate(lines):
        if lineContent.startswith(r"\usepackage"):
            ret.append(line)
    return ret


def CheckUnusedPackages(
        filePath,
        pathToEngine,
        usedPackages=None,
        resultedPath=None,
        verbose=False,
        pathToTemp=None
) -> list[int]:
    # returns the lines that start with \usepackage and don't change output
    # TODO make verbose
    if usedPackages is None: usedPackages = getUsedPackages(filePath)
    if resultedPath is None:
        resultedPath = compileFile(filePath, pathToTemp=pathToTemp, pathToEngine=pathToEngine)
        if resultedPath is None: raise ValueError("Failed to compile file")
    ret = []
    with open(filePath, 'r', encoding="utf-8") as f:
        lines = f.readlines()
    for line in usedPackages:
        print("Checking line", line)
        newLines = lines.copy()
        newLines[line] = "%" + lines[line]
        dirname, basename = os.path.split(filePath)
        with tempfile.NamedTemporaryFile(dir=dirname, prefix=f"line_{line}__") as f:
            f.write("".join(newLines).encode())
            f.seek(0)
            tempCompiled = compileFile(f.name, pathToTemp=pathToTemp, pathToEngine=pathToEngine)
            if tempCompiled is None:
                if verbose: print("Failed to compile file, skipping")
                continue
            if pdf_similar(tempCompiled, resultedPath):
                if verbose: print("Line", line, "is not used")
                ret.append(line)
            else:
                if verbose: print("Line", line, "is used")
    return ret
