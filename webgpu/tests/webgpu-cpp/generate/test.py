#!/usr/bin/python3

import importlib.util
import sys
import os
from os.path import normpath, dirname, join, isfile
import difflib

# -----------------------------------------------------------------------------

class TestFailed(Exception):
    pass

# -----------------------------------------------------------------------------

def main():
    function_main_path = getFunctionMainPath()
    print(f"Testing '{function_main_path}'...")
    assert(isfile(function_main_path))

    function_main = importFunctionMain(function_main_path)

    #testFunctionMainWgpuNative(function_main)
    testFunctionMainDawn(function_main)
    print("Passed.")

# -----------------------------------------------------------------------------

def testFunctionMainWgpuNative(function_main):
    headers = []
    with open("data/wgpu-native/webgpu.h", "r", encoding="utf-8") as f:
        headers.append(f.read())
    with open("data/wgpu-native/wgpu.h", "r", encoding="utf-8") as f:
        headers.append(f.read())
    with open("data/wgpu-native/webgpu.hpp", "r", encoding="utf-8") as f:
        expected_result = f.read()

    result = function_main.main({
        "template": "wgpu-native",
        "headers": headers,
        "use_scoped_enums": True,
        "use_fake_scoped_enums": True,
        "use_non_member_procedures": False,
    }, {})

    if "error" in result["body"]:
        print("Error:")
        raise TestFailed(result["body"]["error"])

    output = result["body"]["output"]
    success = output.strip() == expected_result.strip()

    if not success:
        raise TestFailed("[wgpu-native] Output does not match expected.")

# -----------------------------------------------------------------------------

def testFunctionMainDawn(function_main):
    headers = []
    with open("data/dawn/webgpu.h", "r", encoding="utf-8") as f:
        headers.append(f.read())
    with open("data/dawn/webgpu.hpp", "r", encoding="utf-8") as f:
        expected_result = f.read()

    result = function_main.main({
        "template": "wgpu-native",
        "headers": headers,
        "use_scoped_enums": True,
        "use_fake_scoped_enums": True,
        "use_non_member_procedures": False,
    }, {})

    if "error" in result["body"]:
        print("Error:")
        raise TestFailed(result["body"]["error"])

    output = result["body"]["output"]
    success = output.strip() == expected_result.strip()

    if not success:
        print(diff(output.strip(), expected_result.strip()))
        raise TestFailed("[Dawn] Output does not match expected.")
    print("Passed.")

def diff(actual, expected):
    expected = expected.splitlines(1)
    actual = actual.splitlines(1)
    diff = difflib.unified_diff(expected, actual)
    return ''.join(diff)

# -----------------------------------------------------------------------------

def getFunctionMainPath():
    """
    The function's __main__ is located in a similar directpry as this script,
    except it is "packages" instead of "tests".
    """
    path = normpath(dirname(__file__))
    tokens = path.split(os.sep)
    tokens[-3] = "packages"
    return os.sep.join(tokens + ["__main__.py"])

# -----------------------------------------------------------------------------

def importFunctionMain(function_main_path):
    """
    Import the function's __main__ file as a module
    """
    spec = importlib.util.spec_from_file_location("function_main", function_main_path)
    function_main = importlib.util.module_from_spec(spec)
    sys.modules["function_main"] = function_main
    sys.path.append(dirname(function_main_path))
    spec.loader.exec_module(function_main)
    return function_main

# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
