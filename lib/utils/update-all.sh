for category in $1/*; do
    for subcategory in $category/*; do
        for problem in $subcategory/*; do
            problem_name=$(basename -- "$problem")

            if [ -e "output/$problem_name" ]; then
                echo "Updating $problem..."
                mv $problem/description.md output/$problem_name  
            fi
        done
    done
done
