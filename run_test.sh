coverage erase
coverage run --source=./main/backtrader/ -m pytest ./tests/backtrader/
coverage report -m
coverage html
open ./htmlcov/index.html

