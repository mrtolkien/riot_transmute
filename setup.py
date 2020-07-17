import setuptools
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="riot_transmute",
    version="0.1a16",
    packages=setuptools.find_packages(),
    install_requires=["lol_dto >= 0.1a4"],
    extra_require={"names": ["lol_id_tools"]},
    url="https://github.com/mrtolkien/riot_transmute",
    license="MIT",
    author='Gary "Tolki" Mialaret',
    author_email="gary.mialaret+pypi@gmail.com",
    description="Transmute Riot API objects to the community-defined DTO format.",
    long_description=long_description,
    long_description_content_type="text/markdown",
)
