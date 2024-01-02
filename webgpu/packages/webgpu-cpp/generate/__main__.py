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

    generate_args.template = template + "/webgpu.template.hpp"

    # Output

    generate_args.output = "vfs://output"
    generate_args.virtual_fs["output"] = io.StringIO()

    # Header input

    headers = args.get("headers", [])
    if not headers:
        # Prevent fetching official header by default
        headers = [""]

    generate_args.header_url = []
    for i, header_content in enumerate(headers):
        generate_args.header_url.append(f"vfs://header_url{i}")
        generate_args.virtual_fs[f"header_url{i}"] = io.StringIO(header_content.replace('\r', ''))

    # Defaults

    generate_args.defaults = [
        "defaults.txt",
        "extra-defaults.txt",
    ]

    # Options

    generate_args.pplux = False
    generate_args.use_scoped_enums = bool(args.get("use_scoped_enums", True))
    generate_args.use_fake_scoped_enums = bool(args.get("use_fake_scoped_enums", True))
    generate_args.use_non_member_procedures = bool(args.get("use_non_member_procedures", False))

    return generate_args

# ---------------------------------------------

def runGeneration(generate_args):
    generate.main(generate_args)

# ---------------------------------------------

def getOutput(generate_args):
    return generate_args.virtual_fs["output"].getvalue()

# ---------------------------------------------
