import os
from setuptools import setup, find_packages

def _process_requirements():
    packages = open('requirements.txt').read().strip().split('\n')
    requires = []
    for pkg in packages:
        if pkg.startswith('git+ssh'):
            return_code = os.system('pip install {}'.format(pkg))
            assert return_code == 0, 'error, status_code is: {}, exit!'.format(return_code)
        else:
            requires.append(pkg)
    return requires

setup(
    name='bullet_cli',
    version='0.0.2',
    author="toyops",
    author_email="volqiu@live.com",
    description='watch stock in Terminal',
    install_requires=_process_requirements(),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=['bullet_cli.tencent_stock'],  # 包含 tencent_stock 模块
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'bullet = bullet_cli.main:cli',
        ],
    },
)
