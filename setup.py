import setuptools


setuptools.setup(
    name="triogram",
    version="0.3.2",
    description="Async Telegram Bot API built with httpx and trio",
    packages=setuptools.find_packages("src"),
    package_dir={"": "src"},
    url="https://github.com/rnovatorov/triogram",
    author="Roman Novatorov",
    author_email="roman.novatorov@gmail.com",
    install_requires=["attrs", "httpx==0.12.*", "trio==0.14.*"],
)
