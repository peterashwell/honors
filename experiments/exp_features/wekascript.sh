#/bin/bash
normal_lc_dir="norm_n0.0_a100_m0_s400"
EXPERIMENT_FILE='../experiment_names'
ARFF_DIR='arff'
RES_DIR='raw_results'
SPLITFEAT_DIR='split_feats'
NUM_CLASSES=5
section='#'
while read exp_name
do
	if [[ $exp_name =~ $section ]]; then
		echo "matches section $exp_name"
	else
		if [[ -d $RES_DIR ]]; then
			rm -r $RES_DIR
		fi
		mkdir $RES_DIR

		if [[ -d $ARFF_DIR ]]; then
			rm -r $ARFF_DIR
		fi
		mkdir $ARFF_DIR

		if [[ -d $SPLITFEAT_DIR ]]; then
			rm -r $SPLITFEAT_DIR
		fi
		mkdir $SPLITFEAT_DIR

		if [[ -d $RES_DIR ]]; then
			rm -r $RES_DIR
		fi
		mkdir $RES_DIR

		#echo "matches exp $exp_name"
		echo running experiment $exp_name
		# check that the experiment exists, if not, create the light curves for it

		if [[ -d ${ARFF_DIR}/${exp_name} ]]; then
			rm -r ${ARFF_DIR}/${exp_name}
		fi
		mkdir ${ARFF_DIR}/${exp_name}
		python crossfold.py $normal_lc_dir $exp_name $ARFF_DIR
		
		if [[ -d ${SPLITFEAT_DIR}/${exp_name} ]]; then
			rm -r ${SPLITFEAT_DIR}/${exp_name}
			echo 'removing' ${SPLITFEAT_DIR}/${exp_name}
		fi
		mkdir ${SPLITFEAT_DIR}/${exp_name}
		python split_features.py $exp_name 
		while read feat_name
		do 
			echo classifying with feature $feat_name
			if [[ ! -d ${RES_DIR}/${feat_name} ]]; then
				mkdir ${RES_DIR}/${feat_name}
			fi
			for fold_num in {0..9}
			do
				train=${SPLITFEAT_DIR}/${exp_name}/${feat_name}/train${fold_num}.arff
				test=${SPLITFEAT_DIR}/${exp_name}/${feat_name}/test${fold_num}.arff
				#echo classifying with train $train and test ${test}...
				let head_bound=$NUM_CLASSES
				let tail_bound=$NUM_CLASSES+1
				java -cp /Applications/weka-3-6-4/weka.jar weka.classifiers.trees.RandomForest \
				-t $train -T $test -v | tail -$tail_bound | head -$head_bound > $RES_DIR/${feat_name}/${exp_name}_result${fold_num}
			done
			#echo processing results
			python process_results.py $exp_name $feat_name
		done < 'features.names'
		#rm -r $ARFF_DIR
		rm -r $RES_DIR
	fi
done < $EXPERIMENT_FILE
