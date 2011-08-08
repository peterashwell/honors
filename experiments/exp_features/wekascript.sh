#/bin/bash
normal_lc_dir="norm_n0_a100_m0_s400"
EXPERIMENT_FILE='../experiment_names'
ARFF_DIR='temp_arff'
RES_DIR='temp_results'
SPLITFEAT_DIR='temp_splitfeats'
NUM_CLASSES=5
section='#'
while read line
do
	if [[ $line =~ $section ]]; then
		echo "matches section $line"
	else
		if [[ -d temp_results ]]; then
			rm -r $RES_DIR
		fi
		mkdir $RES_DIR

		if [[ -d temp_arff ]]; then
			rm -r $ARFF_DIR
		fi
		mkdir $ARFF_DIR

		if [[ -d temp_splitfeats ]]; then
			rm -r $SPLITFEAT_DIR
		fi
		mkdir $SPLITFEAT_DIR

		if [[ -d $RES_DIR ]]; then
			rm -r $RES_DIR
		fi
		mkdir $RES_DIR

		#echo "matches exp $line"
		echo running experiment $line
		# check that the experiment exists, if not, create the light curves for it

		python crossfold.py $normal_lc_dir $line $ARFF_DIR
		python split_features.py 
		while read feat_name
		do 
			echo classifying with feature $feat_name
			if [[ ! -d ${RES_DIR}/${feat_name} ]]; then
				mkdir ${RES_DIR}/${feat_name}
			fi
			for fold_num in {0..9}
			do
				train=${SPLITFEAT_DIR}/${feat_name}/train${fold_num}.arff
				test=${SPLITFEAT_DIR}/${feat_name}/test${fold_num}.arff
				#echo classifying with train $train and test ${test}...
				let head_bound=$NUM_CLASSES
				let tail_bound=$NUM_CLASSES+1
				java -cp /Applications/weka-3-6-4/weka.jar weka.classifiers.trees.RandomForest \
				-t $train -T $test -v | tail -$tail_bound | head -$head_bound > $RES_DIR/${feat_name}/${line}_result${fold_num}
			done
			#echo processing results
			python process_results.py $line $feat_name
		done < 'features.names'
		rm -r $ARFF_DIR
		rm -r $RES_DIR
	fi
done < $EXPERIMENT_FILE
