python_sources(
    name="src",
    sources=["cognito_confidential/**/*.py"],
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
    module_mapping={
        "python-jose": ["jose"],
    },
)

resources(
    name="requirements",
    sources=["requirements.txt"],
)

resource(
    name="pyproject",
    source="pyproject.toml",
)

resource(
    name="readme",
    source="README.md",
)

resource(name="version", source="VERSION")

python_distribution(
    name="dist",
    dependencies=[
        ":requirements",
        ":pyproject",
        ":src",
        ":version",
        ":readme",
    ],
    repositories=[
        "@pypi",
    ],
    provides=python_artifact(
        name="artefact",
    ),
    wheel=True,
    sdist=False,
)
