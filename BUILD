py_library(
    name = "p2a_lib",
    srcs = ["p2a_lib.py"],
    srcs_version = "PY3",
    deps = [],
)

py_test(
    name = "p2a_lib_test",
    srcs = ["p2a_lib_test.py"],
    data = [
        "//testdata:input_data",
        "//testdata:output_data",
    ],
    python_version = "PY3",
    deps = [
        ":p2a_lib",
    ],
)

py_binary(
    name = "p2a",
    srcs = ["p2a.py"],
    srcs_version = "PY3",
    deps = [],
)
