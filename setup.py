from setuptools import setup

setup(
    name='tfmesh',
    version='0.1',
    py_modules=['tfmesh'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        tfmesh=tfmesh:cli
    ''',
)