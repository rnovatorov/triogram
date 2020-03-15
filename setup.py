from setuptools import setup, find_packages


setup(
    name="triogram",
    version="0.3.1",
    description="Async Telegram Bot API built with httpx and trio",
    packages=find_packages("src"),
    package_dir={"": "src"},
    url="https://github.com/rnovatorov/triogram",
    author="Roman Novatorov",
    author_email="roman.novatorov@gmail.com",
    install_requires=["attrs", "httpx==0.11.*", "trio==0.13.*", "async_generator"],
)
