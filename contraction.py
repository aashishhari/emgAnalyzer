import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

pd.options.mode.chained_assignment = None  # default='warn'


def originalDataPlotMarkers(df, f, threshold):
	fig, ax = plt.subplots(figsize=(7,3.5))
	df['above_threshold'] = np.where(df['EMG (mV)'] >= threshold, 1, 0) # logic table.
	df["change"] = df['above_threshold'].diff()
	df['change_colors'] = df['change'].map({1:'Red', -1:'Green', 0:np.nan})
	only_changes = df[~pd.isna(df['change_colors'])]
	ax.plot(df['time (s)'], df['EMG (mV)'])
	ax.scatter(only_changes['time (s)'], only_changes['EMG (mV)'], c=only_changes['change_colors'])
	ax.hlines(threshold, min(df['time (s)']), max(df['time (s)']), colors = 'r')
	plt.savefig(f'./emgs/outputs/regular/{f}_regular')
	plt.clf()

	# Save for contraction count later 
	ct = df
	ct = ct.loc[ct['change_colors'] == 'Red']
	return ct


def resampledDataPlotMarkers(df,f, threshold):
	fig, ax = plt.subplots(figsize=(7,3.5))
	micro = pd.date_range('1970-01-01 00:00:01.000000000', '1970-01-01 00:00:01.500000000', freq='us')
	df['time (s)'] = pd.to_datetime(df['time (s)'],unit='s')
	interp = pd.Series(np.interp(micro, df['time (s)'], df['EMG (mV)']))
	interp.index = micro # remove later.
	only_changes = pd.Series(np.where(interp >= threshold, 1, 0)).diff().map({1:'Red', -1:'Green', 0:np.nan})
	only_changes = only_changes[~pd.isna(only_changes)]
	ax.plot(df['time (s)'], df['EMG (mV)'])
	ax.scatter(interp.index[only_changes.index], interp[only_changes.index], c=only_changes)
	ax.hlines(threshold, min(df['time (s)']), max(df['time (s)']), colors = 'r')
	plt.savefig(f'./emgs/outputs/resampled/{f}_resampled')
	plt.clf()


def determineThreshold(df, f):
	'''Returns calculated threshold value'''
	
	scaling = 0 # Scaling Factor Dependent on File
	if 'healthy' in f:
		scaling = 3
	elif 'myopathy' in f:
		scaling = 2
	else:
		scaling = 1
	print(f'Using Scaling Factor: {scaling} ')

	# Calculate Threshold
	sampleInterval = df[(df['time (s)'] >= 1.382) & (df['time (s)']<=1.465)]
	threshold = sampleInterval['EMG (mV)'].mean()+scaling*sampleInterval['EMG (mV)'].std()
	print(f'Calculated Threshold: {threshold}')

	return threshold


def getIndices(df, query):
	'''Source: https://www.geeksforgeeks.org/find-location-of-an-element-in-pandas-dataframe-in-python/'''
	indices = [] 
	result = df.isin([query]) 
	seriesObj = result.any() 
	columnNames = list(seriesObj[seriesObj == True].index) 
	for col in columnNames: 
		rows = list(result[col][result[col] == True].index) 
		for row in rows: 
			indices.append(row)
	return indices 


def findPeaks(df, f):
	redIndices = getIndices(df, 'Red')
	greenIndices = getIndices(df, 'Green')
	peakdf = pd.DataFrame(columns=['time (s)', 'EMG (mV)'])
	for red,green in zip(redIndices, greenIndices):
		interval = df.loc[red:green]
		maxindex = interval[['EMG (mV)']].idxmax()
		row = df.loc[maxindex]
		peakdf = peakdf.append({'time (s)' : str(row['time (s)'].values[0]), 
								'EMG (mV)' : str(row['EMG (mV)'].values[0])},
								ignore_index = True) 
	peakdf.to_csv(f'emgs/outputs/peaks_{f}.csv')

	return len(redIndices)


def countContractions(ct):
	epsilon = 0.01
	numContractions = len(ct)
	ct['timediff'] = (ct['time (s)'].diff(-1))*(-1)
	ct['checkinterval'] = np.where(ct['timediff'] <= epsilon, 1, 0) # logic table
	miscounts = ct['checkinterval'].sum()
	dr = ct.loc[ct['checkinterval']==0]
	duration = dr['timediff'].mean()
	duration = round(duration*1000, 4)
	return numContractions, miscounts, duration


def summary(df,ct,f):
	'''Find Peaks, Count Contractions, Measure Duration, and Print End Messages'''
	
	numIntervals = findPeaks(df,f)
	numContractions, miscounts, duration, = countContractions(ct)
	print(f'{numContractions} Contractions Detected')
	print(f'{miscounts} Miscounts Detected')
	print(f'{numContractions-miscounts} Contractions Estimated')
	print(f'Average Time Duration Between Contractions: {duration} milliseconds')
	print('Contraction Analysis Complete.')
	print('-'*80)
	print(f'{numIntervals} Peaks Found Over {numContractions} Detected Contractions')
	print(f'Peak Info can be found at emgs/outputs/peaks.csv')
	print('Peak Analysis Complete.')


def analyze(df,f):
	'''Start'''

	# Setup
	f = f.strip('.csv')
	plt.style.use('ggplot')
	print('Calculating Threshold Based on Sample Interval: [1.382s - 1.465s] ...')
	
	threshold = determineThreshold(df,f);

	# Plot of Original Data (Regular)
	ct = originalDataPlotMarkers(df, f, threshold) # ct: save for contraction count later.

	# Plot of Resampled Data (Resampled time (s) ==> in order to find more precise time of where EMG crosses threshold)
	resampledDataPlotMarkers(df,f, threshold)

	# Print End Summary
	summary(df,ct,f)
