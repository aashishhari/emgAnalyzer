import contraction
import characterizer
import pandas as pd

def plotly(df,f):
	'''Plots an interactive plot of the dataframe'''
	import plotly.express as px
	fig = px.line(df,x='time (s)',y='EMG (mV)')
	f = f.strip('.csv')
	fig.write_html(f'./emgs/outputs/plotly/{f}_plotly.html')

def mkdir(path):
	'''Creates SubDirectories if Path Does not Exist'''
	from pathlib import Path
	Path(path).mkdir(parents=True, exist_ok=True)

def makepaths():
	'''Creates Output Directories'''
	p1 = 'emgs/outputs/plotly/'
	p2 = 'emgs/outputs/regular/'
	p3 = 'emgs/outputs/resampled/'
	mkdir(p1); mkdir(p2); mkdir(p3)

# Main
def main():
	files = ['emg_healthy.csv','emg_myopathy.csv','emg_neuropathy.csv']
	makepaths()

	for f in files:
		print('*'*80)
		print(f'Analyzing File: {f}')
		print('-'*80)
		# Read
		cols = ['time (s)','EMG (mV)']
		df = pd.read_csv(f'./emgs/{f}',header=None,names=cols)
		#df = df.set_index(['time (s)'])x

		# Edit
		df['EMG (mV)'] = pd.to_numeric(df['EMG (mV)'],errors='coerce') # set any #Name? to NaN value.
		df = df[(df['time (s)']>=1.0) & (df['time (s)']<=1.5)]

		plotly(df,f)

		contraction.analyze(df,f)
		#characterizer.determine(df,f)
		print('-'*80)
		print('All Done!')
		print('*'*80,'\n')


if __name__ == "__main__":
    main()