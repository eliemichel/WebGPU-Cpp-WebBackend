import generate
import argparse
import io
import traceback

# ---------------------------------------------

available_templates = {
    "dawn",
    "emscripten",
    "wgpu-native",
}

class QueryException(Exception):
    pass

# ---------------------------------------------

def main(args, context):
    try:

        generate_args = buildArgs(args)

        runGeneration(generate_args)

        output = getOutput(generate_args)

    except QueryException as err:
        return { "body": { "error": err.message, "type": "runtime" } }
    except Exception as err:
        return { "body": { "error": traceback.format_exc(), "type": "unexpected" } }

    generate_args_dic = vars(generate_args)
    del generate_args_dic["virtual_fs"]

    return {
        "body": {
            #"args": args,
            "generate_args": generate_args_dic,
            "output": output,
        }
    }

# ---------------------------------------------

def buildArgs(args):
    generate_args = argparse.Namespace()
    generate_args.virtual_fs = {}

    # Template

    template = args.get("template", "dawn")
    if template not in available_templates:
        raise QueryException(
            f"Invalid template '{template}', expected values are " +
            ", ".join([f"'{p}'" for p in available_templates]) +
            "."
        )

    if template in { "dawn", "wgpu-native" }:
        # Common template (eventually emscripten will move on to this as well
        # and we'll remove the dropdown list altogether!)
        generate_args.template = "webgpu.template.hpp"
    else:
        generate_args.template = template + "/webgpu.template.hpp"

    # Process

    process = args.get("process", "webgpu-hpp")

    if process == "webgpu-raii-hpp":
        generate_args.template = "webgpu-raii.template.hpp"

    # Output

    generate_args.output = "vfs://output"
    generate_args.virtual_fs["output"] = io.StringIO()

    # Header input

    headers = args.get("headers", [])
    if not headers:
        # Prevent fetching official header by default
        headers = [
            {
                "filename": "webgpu.h",
                "contents": "",
            },
        ]

    generate_args.header_url = []
    for i, header in enumerate(headers):
        path = f"/header_url{i}/" + header["filename"]
        generate_args.header_url.append("vfs://" + path)
        generate_args.virtual_fs[path] = io.StringIO(header["contents"].replace('\r', ''))

    # Defaults

    generate_args.defaults = [
        "defaults.txt",
        "extra-defaults.txt",
    ]

    # Options

    default_use_init_macros = process == "webgpu-hpp" and template == "dawn"

    generate_args.pplux = False
    generate_args.use_scoped_enums = bool(args.get("use_scoped_enums", True))
    generate_args.use_fake_scoped_enums = bool(args.get("use_fake_scoped_enums", True))
    generate_args.use_non_member_procedures = bool(args.get("use_non_member_procedures", False))
    generate_args.use_const = bool(args.get("use_const", True))
    generate_args.use_init_macros = bool(args.get("use_init_macros", default_use_init_macros))
    generate_args.use_inline = bool(args.get("use_inline", False))
    generate_args.ext_suffix = ""

    return generate_args

# ---------------------------------------------

def runGeneration(generate_args):
    generate.main(generate_args)

# ---------------------------------------------

def getOutput(generate_args):
    return generate_args.virtual_fs["output"].getvalue()

# ---------------------------------------------
