# First produce a directory of raw light curves
NUM_LCS=100
LCS=(ESE Novae Noise IDV SNe)
FOOTPRINT="wide"
EXP_FILE="experiment_commands"
RAW_DIR="raw_lightcurves"


if [ -d lightcurves/$RAW_DIR ]; then
	echo 'raw light curve directory exists'
else
	rm lightcurves/*.data
	for lctype in "${LCS[@]}"; do
		python lightcurves/generateLightCurves.py -t $lctype -f $NUM_LCS -n 500 -p $FOOTPRINT -i 0.00000001
	done
	#mkdir lightcurves/$RAW_DIR
	mv *.data $RAW_DIR
fi

# Start applying distortions to raw_lightcurves
while read line
do
	if [[ ! $line =~ ^#.+ ]]; then
		echo distorting with commands $line
		#mkdir lightcurves/$line
		python lightcurves/distort_data.py $line
	fi
done < $EXP_FILE
