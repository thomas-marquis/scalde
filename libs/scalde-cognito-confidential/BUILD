python_sources(
    name="src", 
    sources=["cognito_confidential/**/*.py"],
)

python_tests(
    name="tests", 
    sources=["tests_*/**/test_*.py"],
    dependencies=[
       "//:reqs_dev", 
    ],
)

python_requirements(
    name="reqs",
    module_mapping={
        "python-jose": ["jose"],
    }
)
