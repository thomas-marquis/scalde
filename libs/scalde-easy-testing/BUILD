
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
