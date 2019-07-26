from setuptools import setup, find_packages


setup(
    name="triogram",
    version="0.1.0",
    description="Async Telegram Bot API built with asks and trio",
    packages=find_packages("src"),
    package_dir={"": "src"},
    url="https://github.com/rnovatorov/triogram",
    author="Roman Novatorov",
    author_email="roman.novatorov@gmail.com",
    install_requires=["attrs", "asks", "trio", "async_generator"],
)
