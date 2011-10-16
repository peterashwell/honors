CONFIG_FILE="exp.config"
CROSSFOLD_PATH="crossfold"
SHAPELET_PATH="shapelet"
EXP_DIR=$1

if [[ ! -d $CROSSFOLD_PATH ]]; then
	mkdir $CROSSFOLD_PATH
fi

if [[ ! -d $SHAPELET_PATH ]]; then
	mkdir $SHAPELET_PATH
fi

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
	shapelet_dir="${config[3]}-${config[4]}"
	crossfold_dir="${config[5]}-${config[6]}"
	
	#echo $id
	#echo $param_type
	#echo $param_val
	#echo $shapelet_dir
	#echo $crossfold_dir	
	
	# Check the crossfold directory exists, create if necessary
	if [[ ! -d "${CROSSFOLD_PATH}/${crossfold_dir}" ]]; then
		echo "Crossfold directory ${CROSSFOLD_PATH}/${crossfold_dir} found, creating..."
		python crossfold.py ${config[5]} ${config[6]} ${crossfold_dir}
	else
		echo "Found crossfold directory"
	fi

	# Check the shapelet directory exists, complain if not
	if [[ ! $shapelet_dir =~ "None" ]]; then
		if [[ ! -d "${SHAPELET_PATH}/${shapelet_dir}" ]]; then
			echo "Shapelet directory ${SHAPELET_PATH}/${shapelet_dir} not found"
			echo "Create relevant shapelet directory and run again (exiting...)"
			exit
		fi
	fi

	# Creating experiment directory
	echo Creating directory for experiment ${id}
	#mkdir "$EXP_DIR/$id"

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
