NUM_CLASSES=8
NUM_CROSSFOLDS=10
CLASSIFY_CONFIG="classify.config"
JOIN_FEAT_DIR="joined_features"
EXP_CONFIG="exp.config"
EXP_DIR=$1
RAW_RES_DIR="raw_results"
while read config_line
do
	IFS=","; read -ra config <<< "$config_line"
	id=${config[0]}
	train=${config[5]}
	test=${config[6]}
	crossfold_dir="${config[5]}-${config[6]}"
	while read clsf_config
	do
		IFS=","; read -ra clsf_split <<< "$clsf_config"
		join_id=${clsf_split[0]}
		# Classify the join id crossfolds and store in raw_result
		for (( i = 0; i < $NUM_CROSSFOLDS; i++ ))
		do
			#echo i
			classify_dir="${JOIN_FEAT_DIR}/$crossfold_dir/cf$i/${join_id}"
			out_file="${RAW_RES_DIR}/$crossfold_dir/$join_id/cf$i"
			echo $classify_dir
			echo writing result to $out_file
			if [[ ! -d $RAW_RES_DIR ]]; then
				mkdir $RAW_RES_DIR
			fi

			if [[ ! -d $RAW_RES_DIR/$crossfold_dir ]]; then
				mkdir $RAW_RES_DIR/$crossfold_dir
			fi

			if [[ ! -d $RAW_RES_DIR/$crossfold_dir/$join_id ]]; then
				mkdir $RAW_RES_DIR/$crossfold_dir/$join_id
			fi
			let head_bound=$NUM_CLASSES
			let tail_bound=$NUM_CLASSES+1
			java -cp /Applications/weka-3-6-4/weka.jar weka.classifiers.trees.RandomForest -t $classify_dir/train.arff -T $classify_dir/test.arff\
			 -v | tail -$tail_bound | head -$head_bound > $out_file
		done
	done < "${EXP_DIR}/${CLASSIFY_CONFIG}"
done < "${EXP_DIR}/${EXP_CONFIG}" 

