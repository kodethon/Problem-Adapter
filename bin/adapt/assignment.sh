subcategory=$1
for problem in $subcategory/*; do
    problem_name=$(basename -- "$problem")

    #if [ ! -e "output/$problem_name/cases" ]; then
        echo "Processing $problem..."
        sh problem.sh $problem/$problem_name.py &
    #fi
done
