load("@rules_python//python:defs.bzl", "py_binary", "py_library", "py_test")

package(default_visibility = ["//visibility:public"])

py_library(
    name = "card",
    srcs = ["card.py"],
    srcs_version = "PY3",
    deps = [
        ":frequency",
        ":xml_extractors",
    ],
)

py_test(
    name = "card_test",
    srcs = ["card_test.py"],
    python_version = "PY3",
    deps = [
        ":card",
    ],
)

py_library(
    name = "decomposer",
    srcs = ["decomposer.py"],
    srcs_version = "PY3",
    deps = [
        "//third_party:ids",
    ],
)

py_test(
    name = "decomposer_test",
    srcs = ["decomposer_test.py"],
    python_version = "PY3",
    deps = [
        ":decomposer",
        "@abseil_py//absl/testing:absltest",
    ],
)

py_library(
    name = "converter",
    srcs = ["converter.py"],
    srcs_version = "PY3",
    deps = [
        ":card",
        ":xml_extractors",
        "@abseil_py//absl/logging",
    ],
)

py_test(
    name = "converter_test",
    srcs = ["converter_test.py"],
    data = [
        "//testdata:input_data",
    ],
    python_version = "PY3",
    deps = [
        ":converter",
    ],
)

py_library(
    name = "frequency",
    srcs = ["frequency.py"],
    srcs_version = "PY3",
    deps = [
    ],
)

py_test(
    name = "frequency_test",
    srcs = ["frequency_test.py"],
    python_version = "PY3",
    deps = [
        ":frequency",
        "@abseil_py//absl/testing:absltest",
    ],
)

py_library(
    name = "xml_extractors",
    srcs = ["xml_extractors.py"],
    srcs_version = "PY3",
    deps = [
        "@abseil_py//absl/logging",
    ],
)

py_test(
    name = "xml_extractors_test",
    srcs = ["xml_extractors_test.py"],
    python_version = "PY3",
    deps = [
        ":xml_extractors",
    ],
)

py_library(
    name = "toposorter",
    srcs = ["toposorter.py"],
    srcs_version = "PY3",
    deps = [
        ":card",
        ":decomposer",
    ],
)

py_test(
    name = "toposorter_test",
    srcs = ["toposorter_test.py"],
    python_version = "PY3",
    deps = [
        ":toposorter",
        "@abseil_py//absl/testing:absltest",
    ],
)

py_binary(
    name = "main",
    srcs = ["main.py"],
    srcs_version = "PY3",
    data = [
        "//third_party:hsk",
    ],
    deps = [
        ":anki_utils",
        ":converter",
        ":decomposer",
        ":frequency",
        ":hsk_utils",
        ":toposorter",
        "@abseil_py//absl:app",
        "@abseil_py//absl/flags",
    ],
)

py_library(
    name = "anki_utils",
    srcs = ["anki_utils.py"],
    srcs_version = "PY3",
    deps = [
        ":card",
        ":hsk_utils",
        ":decomposer",
    ],
)

py_test(
    name = "anki_utils_test",
    srcs = ["anki_utils_test.py"],
    python_version = "PY3",
    deps = [
        ":anki_utils",
        "@abseil_py//absl/testing:absltest",
    ],
)

py_library(
    name = "hsk_utils",
    srcs = ["hsk_utils.py"],
    srcs_version = "PY3",
    data = ["//third_party:hsk"],
    deps = [
    ],
)

py_test(
    name = "hsk_utils_test",
    srcs = ["hsk_utils_test.py"],
    python_version = "PY3",
    deps = [
        ":hsk_utils",
        "@abseil_py//absl/testing:absltest",
    ],
)
