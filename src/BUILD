load("@rules_python//python:defs.bzl", "py_library", "py_test", "py_binary")

package(default_visibility = ["//visibility:public"])

py_library(
    name = "card",
    srcs = ["card.py"],
    srcs_version = "PY3",
    deps = [
        ":defn_extractor",
        ":pinyin",
        ":xml_extractors",
        ":frequency",
        ":sound",
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
    name="decomposer",
    srcs=["decomposer.py"],
    srcs_version="PY3",
    deps=[
        "//third_party:ids"
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
    name = "defn_extractor",
    srcs = ["defn_extractor.py"],
    srcs_version = "PY3",
    deps = [
    ],
)

py_test(
    name = "defn_extractor_test",
    srcs = ["defn_extractor_test.py"],
    python_version = "PY3",
    deps = [
        ":defn_extractor",
    ],
)

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
        ":card",
        ":frequency",
        ":pinyin",
        ":sound",
        ":xml_extractors",
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
        ":decomposer",
        ":card",
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
    deps = [
        ":anki_utils",
        ":decomposer",
        ":frequency",
        ":toposorter",
        ":converter",
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