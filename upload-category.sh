category=$1
for problem in $category/*; do
    problem_name=$(basename -- "$problem")
    python lib/upload.py output/$problem_name
done
