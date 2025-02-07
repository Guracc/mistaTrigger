from setuptools import setup

APP = ["mistaTrigger.py"]
DATA_FILES = []
OPTIONS = {
    "argv_emulation": False,
    "packages": ["numpy", "scipy"],
    "iconfile": "price_tag.png",
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
