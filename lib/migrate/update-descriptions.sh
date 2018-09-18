dist_path=../../dist
for problem in $1/*; do
    problem_name=$(basename -- "$problem")
    if [ -e "$dist_path/$problem_name" ]; then
        echo "Updating description for $problem..."
        mv $problem/description.md $dist_path/$problem_name  
    fi
done
