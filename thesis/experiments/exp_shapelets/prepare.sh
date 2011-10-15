CONFIG_FILE="exp.config"
CROSSFOLD_PATH="crossfold"
SHAPELET_PATH="shapelet"
EXP_DIR=$1

while read config_line
do
	echo $config_line
	IFS=","; read -ra config <<< "$config_line"
	#for p in ${config[@]}
	#do
	#	echo "> $p"
	#done
	
	id=${config[0]}
	param_type=${config[1]}
	param_val=${config[2]}
	shapelet_dir="${config[3]}_${config[4]}_${config[5]}"
	crossfold_dir="${config[6]}_${config[7]}"
	
	#echo $id
	#echo $param_type
	#echo $param_val
	#echo $shapelet_dir
	#echo $crossfold_dir	
	
	# Check the crossfold directory exists, create if necessary
	if [[ ! -d "${CROSSFOLD_PATH}/${crossfold_dir}" ]]; then
		echo "Crossfold directory ${CROSSFOLD_PATH}/${crossfold_dir} found, creating..."
		python crossfold.py ${config[6]} ${config[7]} ${crossfold_dir}
	else
		echo "Found crossfold directory"
	fi

	# Check the shapelet directory exists, complain if not
	if [[ ! -d "${SHAPELET_PATH}/${shapelet_dir}" ]]; then
		echo "Shapelet directory ${SHAPELET_PATH}/${shapelet_dir} not found"
		echo "Create relevant shapelet directory and run again (exiting...)"
		exit
	fi

	# Creating experiment directory
	echo Creating directory for experiment ${id}
	mkdir "$EXP_DIR/$id"
	mkdir "${EXP_DIR}/${id}/arff"
	mkdir "${EXP_DIR}/${id}/result"

	# Use script with features.config to extract features to arff per crossfold
	python extract_features.py $EXP_DIR 

	# Run classification script on arff and store values in result
	./classify.sh $EXP_DIR

	# Accumulate results
	python accumulate.py $EXP_DIR
	
	mkdir "${EXP_DIR}/${id}/tex"

	# Produce a page of plots summarising results
	python plots.py $EXP_DIR
done < "${EXP_DIR}/${CONFIG_FILE}"
