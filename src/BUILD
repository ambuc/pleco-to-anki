load("@rules_python//python:defs.bzl", "py_library", "py_test")

package(default_visibility = ["//visibility:public"])

py_library(
    name = "tone",
    srcs = ["tone.py"],
    srcs_version = "PY3",
    deps = [
    ],
)

py_library(
    name = "converter",
    srcs = ["converter.py"],
    srcs_version = "PY3",
    deps = [
        ":frequency",
        ":pinyin",
        ":sound",
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

py_library(
    name = "pinyin",
    srcs = ["pinyin.py"],
    srcs_version = "PY3",
    deps = [
        ":tone",
    ],
)

py_library(
    name = "sound",
    srcs = ["sound.py"],
    srcs_version = "PY3",
    deps = [
        ":tone",
    ],
)

py_test(
    name = "pinyin_test",
    srcs = ["pinyin_test.py"],
    python_version = "PY3",
    deps = [
        ":pinyin",
    ],
)

py_library(
    name = "frequency",
    srcs = ["frequency.py"],
    srcs_version = "PY3",
    deps = [
        ":tone",
    ],
)

py_test(
    name = "is_cjk_test",
    srcs = ["is_cjk_test.py"],
    python_version = "PY3",
    deps = [
        ":is_cjk",
    ],
)

py_library(
    name = "is_cjk",
    srcs = ["is_cjk.py"],
    srcs_version = "PY3",
    deps = [
        ":tone",
    ],
)
