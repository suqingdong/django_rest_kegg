rm -rf build dist *.egg-info
python3 setup.py build sdist bdist_wheel
python3 -m twine check dist/*

rm -rf build *.egg-info

echo 'python3 -m twine upload dist/*'
