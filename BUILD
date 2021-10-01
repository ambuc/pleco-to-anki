load("@rules_python//python:defs.bzl", "py_binary")

py_binary(
    name = "p2a",
    srcs = ["p2a.py"],
    srcs_version = "PY3",
    deps = [
        "//src:converter",
        "@abseil_py//absl:app",
        "@abseil_py//absl/flags",
    ],
)

sh_test(
    name = "p2a_test",
    srcs = ["p2a_test.sh"],
    data = [
        ":p2a",
        "//testdata:input_data",
        "//testdata:output_data",
    ],
)

py_binary(
    name = "video2anki",
    srcs = ["video2anki.py"],
    srcs_version = "PY3",
    deps = [
        "@abseil_py//absl:app",
        "@abseil_py//absl/flags",
    ],
)

py_binary(
    name = "toposort",
    srcs = ["toposort.py"],
    srcs_version = "PY3",
    deps = [
        "//src:card",
        "@abseil_py//absl:app",
        "@abseil_py//absl/flags",
    ],
)