for category in $1/*; do
    for subcategory in $category/*; do
        for problem in $subcategory/*; do
            echo "Processing $problem..."

            problem_name=$(basename -- "$problem")
            sh adapt-one.sh $problem/$problem_name.py
        done
    done
done
