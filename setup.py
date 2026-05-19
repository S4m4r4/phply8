from setuptools import setup, find_packages

setup(
    name="phply8",
    version="1.3.0",
    packages=find_packages(exclude=["tests*", "da_training_project_tests*",
                                     "MISC*", "tools*", "php_interpreter*"]),
    include_package_data=True,
    description="PHP 8.x lexer and parser for Python, built on PLY",
    license="BSD",
    zip_safe=False,
    platforms="any",
    python_requires=">=3.8",

    entry_points={
        "console_scripts": [
            "phply8=phply.__main__:main",
        ],
    },

    install_requires=[
        "ply",
    ],

    extras_require={
        "test": ["pytest"],
    },
)
