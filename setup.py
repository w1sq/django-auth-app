from setuptools import setup, find_packages

setup(
    name="django-auth-app",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "Django",
        "djangorestframework",
        "PyJWT",
        "django-constance",
        "django-cors-headers",
        "drf-yasg",
    ],
    python_requires=">=3.11",
)
