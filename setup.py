import setuptools

setuptools.setup(
    name="Fizzier",
    version="0.1.0",
    author="Franca Ellerman",
    description="One-way sync your Google Classroom assignments to your to-do list",
    #long_description=long_description,
    #long_description_content_type="text/markdown",
    url="https://github.com/francaellerman/fizzier",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

