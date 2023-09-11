#!/bin/bash

if [ -d dml ]; then
	echo "dml results dir already exists, please remove or move results before running"
	exit
fi

rm -f *.txt


NTHREADS=(1 2 4 8)
DSA_CONFIGS=("1n1d4e1w-s-n1.conf" "1n2d4e1w-s-n1.conf" "1n4d4e1w-s-n1.conf" "2n1d4e1w-s.conf" "2n2d4e1w-s.conf" "2n4d4e1w-s.conf") 
DSA_CONFIGS_STR=("1-1" "1-2" "1-4" "2-1" "2-2" "2-4")
NRUNS=1
LOWR=2000000
HIGHR=2000000
ACCEL_CONF=/home/user/Src/DML/tools/

for j in `seq 0 $(( ${#DSA_CONFIGS[@]} - 1 ))`; do
	python3 $ACCEL_CONF/scripts/accel_conf.py --load=$ACCEL_CONF/configs/${DSA_CONFIGS[$j]}

	if [ $? -ne 0 ]; then
		echo "failed to configure dsa for ${DSA_CONFIGS[@]}"
		exit
	fi

	for nthreads in ${NTHREADS[@]}; do
		with_dml_dir=dml/with-dml-$LOWR-$HIGHR-$nthreads-${DSA_CONFIGS_STR[$j]}
		mkdir -p $with_dml_dir

		for i in $(seq 1 $NRUNS); do
			echo "Running ${with_dml_dir} for run $i"
			sudo DOTNET_gcServer=1 DOTNET_GCHeapCount=c DOTNET_gcUseDML=1 LD_LIBRARY_PATH=/lib64 /home/user/dotnet/runtime/artifacts/tests/coreclr/linux.x64.Release/Tests/Core_Root/corerun artifacts/bin/GCPerfSim/Release/net7.0/GCPerfSim.dll -tc $nthreads -tagb 500 -tlgb 10 -lohar 900 -lohsr $LOWR-$HIGHR > run-$i.log
			if [ $? -ne 0 ]; then
				echo "failed to run subcase"
				exit
			fi


			mv *.txt $with_dml_dir/run-$i.txt
			mv run-$i.log $with_dml_dir/run-$i.log
		done

		no_dml_dir=dml/no-dml-$LOWR-$HIGHR-$nthreads-${DSA_CONFIGS_STR[$j]}
		mkdir -p $no_dml_dir

		for i in $(seq 1 $NRUNS); do
			echo "Running ${no_dml_dir} for run $i"
			sudo DOTNET_gcServer=1 DOTNET_GCHeapCount=c DOTNET_gcUseDML=0 LD_LIBRARY_PATH=/lib64 /home/user/dotnet/runtime/artifacts/tests/coreclr/linux.x64.Release/Tests/Core_Root/corerun artifacts/bin/GCPerfSim/Release/net7.0/GCPerfSim.dll -tc $nthreads -tagb 500 -tlgb 10 -lohar 900 -lohsr $LOWR-$HIGHR > run-$i.log
			if [ $? -ne 0 ]; then
				echo "failed to run subcase"
				exit
			fi
			mv *.txt $no_dml_dir/run-$i.txt
			mv run-$i.log $no_dml_dir/run-$i.log
		done
	done
done