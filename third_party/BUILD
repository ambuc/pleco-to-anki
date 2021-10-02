load("@rules_python//python:defs.bzl", "py_library")

package(default_visibility = ["//visibility:public"])

filegroup(
    name = "ids_txt",
    srcs = [
        "IDS.txt",
    ],
    visibility = ["//visibility:public"],
)


py_library(
    name = "ids",
    srcs = ["ids.py"],
    srcs_version = "PY3",
    data = [":ids_txt"],
    deps = [
    ],
)
