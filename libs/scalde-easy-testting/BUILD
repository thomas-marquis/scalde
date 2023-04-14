python_sources(
    name="src", 
    sources=[
        "easy_testing/**/*.py",
    ],
)

python_tests(
    name="tests", 
    sources=["tests_*/**/test_*.py"],
    dependencies=[
       "//:reqs_dev", 
       ":reqs",
       ":src",
    ],
)

python_requirements(
    name="reqs",
)
