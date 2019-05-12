from setuptools import setup, find_packages


setup(
    name='triogram',
    version='0.0.1',
    description='Async Telegram Bot API built with asks and trio',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/rnovatorov/triogram',
    author='Roman Novatorov',
    author_email='roman.novatorov@gmail.com',
    # TODO: Bump version when asks gets session instantiation fixed:
    #   https://github.com/theelous3/asks/pull/120
    install_requires=['asks==2.2.1', 'trio', 'async_generator']
)
