for category in $1/*; do
    for subcategory in $category/*; do
        for problem in $subcategory/*; do
            problem_name=$(basename -- "$problem")

            if [ -e "output/$problem_name" ]; then
                echo "Processing $problem..."
                sh adapt-one.sh $problem/$problem_name.py
            fi
        done
    done
done
