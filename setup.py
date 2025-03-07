from setuptools import setup, find_packages

setup(
    name="toast-exports-etl",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "pandas",
        "python-dotenv",
        "psycopg[binary]",
    ],
    extras_require={
        "dev": ["pytest"],
    },
) 