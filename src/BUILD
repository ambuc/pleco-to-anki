package(default_visibility = ["//visibility:public"])

py_library(
    name = "converter",
    srcs = ["converter.py"],
    srcs_version = "PY3",
    deps = [
        "@abseil_py//absl/logging",
    ],
)

py_test(
    name = "converter_test",
    srcs = ["converter_test.py"],
    data = [
        "//testdata:input_data",
        "//testdata:output_data",
    ],
    python_version = "PY3",
    deps = [
        ":converter",
    ],
)
