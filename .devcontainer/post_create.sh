sudo apt-get update
sudo apt-get install -y libaspell-dev

pip install --upgrade \
    aspell-python-py3 \
    pip \
    setuptools \
    setuptools_scm \
    wheel
pip install -e '.[dev]'

pre-commit install --install-hooks
