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
    ]
)
