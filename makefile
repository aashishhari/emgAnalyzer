start:
	python3 main.py

clean:
	rm -rf ./emgs/outputs/*

gitrestore:
	git restore emgs/outputs/plotly/*	