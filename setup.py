import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mongoEngineLock",
    version="0.1.0",
    author="Abhishek Tamrakar",
    author_email="abhishek.tamrakar08@gmail.com",
    description="Mongoengine pessimistic lock utility",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/abhiTamrakar/PessimisticMongo",
    packages=setuptools.find_packages(),
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "pymongo>=3.7.2",
        "mongoengine>=0.16.3"
    ],
    py_modules=["mongoEngineLock"],
    setup_requires=["pytest-runner", "flake8"],
    tests_require=["pytest", "flake8"]
)
