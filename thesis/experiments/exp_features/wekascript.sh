#!/bin/bash
normal_lc_dir="norm_n0.0_a100_m0_s400"
EXPERIMENT_FILE='../experiment_names'
ARFF_DIR='arff'
RES_DIR='raw_results'
SPLITFEAT_DIR='split_feats'
NUM_CLASSES=8
section='#'
CACHEFILE='features.cache'

# Check to see if the cache exists, make it otherwise
if [[ ! -f $CACHEFILE ]]; then
	touch $CACHEFILE
fi

# Clear feature-split arff file directory
if [[ -d $SPLITFEAT_DIR ]]; then
	rm -r $SPLITFEAT_DIR
fi
mkdir $SPLITFEAT_DIR

# Clear previous arff file directory
if [[ -d $ARFF_DIR ]]; then
	rm -r $ARFF_DIR
fi
mkdir $ARFF_DIR

# Carry out each experiment, by its systematic name
let cropped=0
while read exp_name
do
	if [[ $exp_name =~ $section ]]; then
		let cropped=0 # don't reset for each experiment
		echo "matches section $exp_name"
		if [[ $exp_name =~ '#as' ]]; then
			let cropped=1
			echo 'classifying from cropped training curves'
		fi
	else
		# Clear previous result directory
		if [[ -d $RES_DIR ]]; then
			rm -r $RES_DIR
		fi
		mkdir $RES_DIR
		
		#echo "matches exp $exp_name"
		echo running experiment $exp_name
		# check that the experiment exists, if not, create the light curves for it
		
		# Clear previous ARFF dir (it will have old features)
		if [[ -d ${ARFF_DIR}/${exp_name} ]]; then
			rm -r ${ARFF_DIR}/${exp_name}
		fi
		mkdir ${ARFF_DIR}/${exp_name}
	
		# Identify the names of the directories containing the training and test light curves	
		train_dir=${normal_lc_dir}
		test_dir=${exp_name}
		# Take the crop mark out of the experiment name, and find the appropriate cropped training light curves
		if [[ $cropped == 1 ]]; then
			crop_amt=`echo $exp_name | sed 's/.*a\([0-9]*\)_.*/\1/g'`
			train_dir="norm_n0.0_a${crop_amt}_m0_s400" # save some time not doing this twice
			test_dir=`echo $exp_name | sed 's/_c//g'`
			echo "test dir: ${test_dir}$"
			echo "training dir: ${train_dir}$"
		fi
	
		python crossfold.py $train_dir $test_dir $ARFF_DIR $exp_name
		
		if [[ -d ${SPLITFEAT_DIR}/${exp_name} ]]; then
			rm -r ${SPLITFEAT_DIR}/${exp_name}
			echo 'removing' ${SPLITFEAT_DIR}/${exp_name}
		fi
		mkdir ${SPLITFEAT_DIR}/${exp_name}
		
		# Split up the arff files according to each feature
		python split_feats.py $exp_name 

		# Classify the arff data based on the feature using RandomForest
		while read feat_name
		do 
			echo classifying with feature $feat_name
			if [[ ! -d ${RES_DIR}/${feat_name} ]]; then
				mkdir ${RES_DIR}/${feat_name}
			fi
			for fold_num in {0..9}
			do
				# TODO identify the training directory correctly in the case of cropped training data
				train=${SPLITFEAT_DIR}/${exp_name}/${feat_name}/train${fold_num}.arff
				test=${SPLITFEAT_DIR}/${exp_name}/${feat_name}/test${fold_num}.arff
				#echo classifying with train $train and test ${test}...
				let head_bound=$NUM_CLASSES
				let tail_bound=$NUM_CLASSES+1
				#echo head_bound $head_bound
				#echo tail_bound $tail_bound
				# Store the raw confusion matrix result in the raw_result directory
				# TODO add an if statement to classify with the reduced featureset here
				java -cp /Applications/weka-3-6-4/weka.jar weka.classifiers.trees.RandomForest \
				-t $train -T $test -v | tail -$tail_bound | head -$head_bound > $RES_DIR/${feat_name}/${exp_name}_result${fold_num}
			done
			# Process the results into metrics per class etc
			python process_results.py $exp_name $feat_name
		done < 'features.names'
	fi
done < $EXPERIMENT_FILE

# Produce the report
python produce_plots.py
#pdflatex results.tex
rm -f *.log
rm -f *.dvi
rm -f *.ps
rm -f *.aux
rm -f *.out
