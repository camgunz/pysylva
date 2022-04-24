from setuptools import setup, find_packages


setup(
    name="Sylva",
    version="0.0.1",
    packages=find_packages(),
    scripts=['scripts/sylva'],
    package_data={'sylva': ['Sylva.lark']},

    # metadata to display on PyPI
    author="Charlie Gunyon",
    author_email="charles.gunyon@gmail.com",
    description="Compiler for the Sylva programming language",
    keywords="sylva compiler",
    url="https://github.com/camgunz/pysylva/",
    project_urls={
        "Source Code": "https://gitub.com/camgunz/pysylva",
    },
    classifiers=['License :: OSI Approved :: MIT']
)
