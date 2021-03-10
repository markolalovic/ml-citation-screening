VENV := longevity-research-screening-venv

run:
	python3 -m venv $(VENV)
	./$(VENV)/bin/pip install -r requirements.txt
	./$(VENV)/bin/python3 preprocess_articles.py
	./$(VENV)/bin/python3 evaluate_performance.py
	./$(VENV)/bin/python3 export_results.py

full:
	python3 -m venv $(VENV)
	./get_chromedriver.sh
	./get_mallet.sh
	./$(VENV)/bin/pip install -r requirements.txt
	./$(VENV)/bin/python3 preprocess_articles.py
	./$(VENV)/bin/python3 evaluate_performance.py full
	./$(VENV)/bin/python3 export_results.py full

clean:
	rm -rf $(VENV)
	find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete
	rm ../models/*
	rm ./chromedriver
	rm -rf ./Mallet/

.PHONY: run full
