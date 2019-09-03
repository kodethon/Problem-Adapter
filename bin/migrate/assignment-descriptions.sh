dist_path=$2
for problem in $1/*; do
    problem_name=$(basename -- "$problem")
    if [ -e "$dist_path/$problem_name" ]; then
        command="cp $problem/description.md $dist_path/$problem_name"
        echo $command
        $command
    else
        #echo "$dist_path/$problem_name does not exist..."
        cp -r $problem $dist_path
    fi
done
